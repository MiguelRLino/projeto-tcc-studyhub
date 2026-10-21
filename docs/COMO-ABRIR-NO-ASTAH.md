# Como abrir o Diagrama de Classes no Astah

Arquivo: `diagrama-classes-studyhub.puml`

O Astah **não abre `.puml` com duplo clique**. É preciso importar pelo plugin PlantUML (ou colar o texto na PlantUML View).

## Passo a passo

1. Abra o **Astah UML** ou **Astah Professional** (versão 10+ recomendada).
2. Instale o plugin PlantUML (se ainda não tiver):
   - Baixe em: https://astah.net/product-plugins/plantuml-plugin/
   - Arraste o `.jar` para a janela do Astah e reinicie.
3. Crie um projeto novo: **File → New**.
4. Ative a aba: **View → Show/Hide Extra View → PlantUML View**.
5. Abra o arquivo `diagrama-classes-studyhub.puml` no Bloco de Notas (ou no Cursor), copie **todo** o conteúdo.
6. Cole na **PlantUML View**.
7. Clique em **▲ toAstah**.

Pronto: o diagrama de classes será criado no projeto. Depois salve normalmente como `.asta` (**File → Save**).

## Observação

Não é possível gerar um `.asta` nativo “pronto” fora do Astah de forma confiável; o `.puml` é o formato intermediário oficial para isso.
