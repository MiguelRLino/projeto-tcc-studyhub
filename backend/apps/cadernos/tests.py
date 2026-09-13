from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.alunos.models import Aluno
from apps.alunos.services.auth_service import criar_token_acesso
from apps.cadernos.models import Caderno, PaginaCaderno
from apps.sistema_estudos.models import LogAtividade


class CadernosAPITestCase(APITestCase):
    def setUp(self):
        self.aluno_a = Aluno.objects.create(
            nome="Aluno A",
            email="a@test.com",
            senha=make_password("senha123"),
        )
        self.aluno_b = Aluno.objects.create(
            nome="Aluno B",
            email="b@test.com",
            senha=make_password("senha123"),
        )
        self.token_a = criar_token_acesso(self.aluno_a.pk)
        self.token_b = criar_token_acesso(self.aluno_b.pk)
        self.auth_a = {"HTTP_AUTHORIZATION": f"Bearer {self.token_a}"}
        self.auth_b = {"HTTP_AUTHORIZATION": f"Bearer {self.token_b}"}

    def test_listar_cadernos_exige_autenticacao(self):
        res = self.client.get("/api/cadernos/")
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_criar_e_listar_caderno(self):
        res = self.client.post(
            "/api/cadernos/",
            {"titulo": "Banco de Dados", "cor": "#6366f1"},
            format="json",
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["titulo"], "Banco de Dados")

        lista = self.client.get("/api/cadernos/", **self.auth_a)
        self.assertEqual(lista.status_code, status.HTTP_200_OK)
        self.assertEqual(len(lista.data), 1)

        log = LogAtividade.objects.filter(acao="CRIAR_CADERNO", aluno=self.aluno_a).first()
        self.assertIsNotNone(log)

    def test_editar_caderno(self):
        caderno = Caderno.objects.create(aluno=self.aluno_a, titulo="Original")
        res = self.client.patch(
            f"/api/cadernos/{caderno.pk}/",
            {"titulo": "Editado"},
            format="json",
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        caderno.refresh_from_db()
        self.assertEqual(caderno.titulo, "Editado")

    def test_soft_delete_caderno_e_paginas(self):
        caderno = Caderno.objects.create(aluno=self.aluno_a, titulo="Excluir")
        pagina = PaginaCaderno.objects.create(
            caderno=caderno,
            titulo="Página",
            conteudo={"type": "doc", "content": []},
        )
        res = self.client.delete(f"/api/cadernos/{caderno.pk}/", **self.auth_a)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        caderno.refresh_from_db()
        pagina.refresh_from_db()
        self.assertIsNotNone(caderno.data_exclusao)
        self.assertIsNotNone(pagina.data_exclusao)

        lista = self.client.get("/api/cadernos/", **self.auth_a)
        self.assertEqual(len(lista.data), 0)

    def test_isolamento_entre_alunos(self):
        caderno = Caderno.objects.create(aluno=self.aluno_a, titulo="Privado")
        res = self.client.get(f"/api/cadernos/{caderno.pk}/", **self.auth_b)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_criar_pagina_e_atualizar_conteudo(self):
        caderno = Caderno.objects.create(aluno=self.aluno_a, titulo="Mat")
        conteudo = {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Normalização SQL"}],
                }
            ],
        }
        res = self.client.post(
            f"/api/cadernos/{caderno.pk}/paginas/",
            {"titulo": "Normalização", "conteudo": conteudo},
            format="json",
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        pagina_id = res.data["id_pagina"]
        self.assertGreater(res.data["quantidade_palavras"], 0)

        patch = self.client.patch(
            f"/api/paginas/{pagina_id}/",
            {
                "conteudo": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "Texto atualizado autosave"}
                            ],
                        }
                    ],
                }
            },
            format="json",
            **self.auth_a,
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(patch.data["quantidade_palavras"], 2)

    def test_duplicar_mover_favoritar_pagina(self):
        c1 = Caderno.objects.create(aluno=self.aluno_a, titulo="Origem")
        c2 = Caderno.objects.create(aluno=self.aluno_a, titulo="Destino")
        pagina = PaginaCaderno.objects.create(
            caderno=c1,
            titulo="Funções",
            conteudo={"type": "doc", "content": []},
        )

        dup = self.client.post(f"/api/paginas/{pagina.pk}/duplicar/", **self.auth_a)
        self.assertEqual(dup.status_code, status.HTTP_201_CREATED)
        self.assertIn("(cópia)", dup.data["titulo"])

        fav = self.client.patch(
            f"/api/paginas/{pagina.pk}/favoritar/",
            {"favorita": True},
            format="json",
            **self.auth_a,
        )
        self.assertTrue(fav.data["favorita"])

        mover = self.client.post(
            f"/api/paginas/{pagina.pk}/mover/",
            {"caderno_destino_id": c2.pk},
            format="json",
            **self.auth_a,
        )
        self.assertEqual(mover.status_code, status.HTTP_200_OK)
        self.assertEqual(mover.data["id_caderno"], c2.pk)

    def test_pesquisar_paginas(self):
        caderno = Caderno.objects.create(aluno=self.aluno_a, titulo="BD")
        PaginaCaderno.objects.create(
            caderno=caderno,
            titulo="Normalização",
            conteudo={
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "primeira forma normal"}],
                    }
                ],
            },
        )
        res = self.client.get(
            "/api/paginas/pesquisar/",
            {"q": "primeira"},
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_reordenar_paginas(self):
        caderno = Caderno.objects.create(aluno=self.aluno_a, titulo="Ordem")
        p1 = PaginaCaderno.objects.create(
            caderno=caderno, titulo="A", ordem=1, conteudo={"type": "doc", "content": []}
        )
        p2 = PaginaCaderno.objects.create(
            caderno=caderno, titulo="B", ordem=2, conteudo={"type": "doc", "content": []}
        )
        res = self.client.post(
            f"/api/cadernos/{caderno.pk}/paginas/reordenar/",
            {
                "ordens": [
                    {"id_pagina": p1.pk, "ordem": 2},
                    {"id_pagina": p2.pk, "ordem": 1},
                ]
            },
            format="json",
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        p1.refresh_from_db()
        p2.refresh_from_db()
        self.assertEqual(p1.ordem, 2)
        self.assertEqual(p2.ordem, 1)

    def test_exportar_pdf_registra_log(self):
        caderno = Caderno.objects.create(aluno=self.aluno_a, titulo="PDF")
        pagina = PaginaCaderno.objects.create(
            caderno=caderno,
            titulo="Export",
            conteudo={"type": "doc", "content": []},
        )
        res = self.client.post(
            f"/api/paginas/{pagina.pk}/exportar-pdf/",
            **self.auth_a,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        log = LogAtividade.objects.filter(acao="EXPORTAR_PDF", aluno=self.aluno_a).first()
        self.assertIsNotNone(log)

    def test_aluno_b_nao_acessa_pagina_de_aluno_a(self):
        caderno = Caderno.objects.create(aluno=self.aluno_a, titulo="X")
        pagina = PaginaCaderno.objects.create(
            caderno=caderno,
            titulo="Y",
            conteudo={"type": "doc", "content": []},
        )
        res = self.client.patch(
            f"/api/paginas/{pagina.pk}/",
            {"titulo": "Hack"},
            format="json",
            **self.auth_b,
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
