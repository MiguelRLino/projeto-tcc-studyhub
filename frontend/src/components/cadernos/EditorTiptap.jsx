import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import TextAlign from "@tiptap/extension-text-align";
import { Color } from "@tiptap/extension-color";
import { TextStyle } from "@tiptap/extension-text-style";
import FontFamily from "@tiptap/extension-font-family";
import Highlight from "@tiptap/extension-highlight";
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";
import { Table } from "@tiptap/extension-table";
import { TableRow } from "@tiptap/extension-table-row";
import { TableCell } from "@tiptap/extension-table-cell";
import { TableHeader } from "@tiptap/extension-table-header";
import Subscript from "@tiptap/extension-subscript";
import Superscript from "@tiptap/extension-superscript";
import TaskList from "@tiptap/extension-task-list";
import TaskItem from "@tiptap/extension-task-item";
import Placeholder from "@tiptap/extension-placeholder";
import { useEffect, useImperativeHandle, forwardRef, useMemo } from "react";
import { FontSize } from "./extensions/FontSize";
import { CONTEUDO_VAZIO, normalizarConteudo } from "../../utils/cadernoMetricas";

const extensoes = (placeholder) => [
  StarterKit.configure({
    heading: { levels: [1, 2, 3, 4] },
  }),
  Underline,
  TextStyle,
  FontSize,
  FontFamily,
  Color,
  Highlight.configure({ multicolor: true }),
  TextAlign.configure({ types: ["heading", "paragraph"] }),
  Link.configure({ openOnClick: false, autolink: true }),
  Image.configure({ inline: false, allowBase64: false }),
  Table.configure({ resizable: true }),
  TableRow,
  TableHeader,
  TableCell,
  Subscript,
  Superscript,
  TaskList,
  TaskItem.configure({ nested: true }),
  Placeholder.configure({ placeholder }),
];

const EditorTiptap = forwardRef(function EditorTiptap(
  { conteudo, onChange, onEditorReady, paperRef, zoom = 100, readOnly = false },
  ref,
) {
  const conteudoSeguro = useMemo(
    () => normalizarConteudo(conteudo),
    [conteudo],
  );

  const extensions = useMemo(
    () => extensoes("Comece a escrever suas anotações…"),
    [],
  );

  const editor = useEditor({
    extensions,
    content: conteudoSeguro,
    editable: !readOnly,
    immediatelyRender: false,
    onUpdate: ({ editor: ed }) => {
      onChange?.(ed.getJSON());
    },
    editorProps: {
      attributes: {
        class: "caderno-editor-prose",
      },
    },
  });

  useImperativeHandle(ref, () => ({
    getEditor: () => editor,
    getJSON: () => editor?.getJSON(),
    setContent: (json) =>
      editor?.commands.setContent(normalizarConteudo(json), { emitUpdate: false }),
    insertImage: (url) => editor?.chain().focus().setImage({ src: url }).run(),
  }));

  useEffect(() => {
    if (editor) onEditorReady?.(editor);
  }, [editor, onEditorReady]);

  useEffect(() => {
    if (!editor || conteudo == null) return;
    const atual = JSON.stringify(editor.getJSON());
    const novo = JSON.stringify(conteudoSeguro);
    if (atual !== novo) {
      editor.commands.setContent(conteudoSeguro, { emitUpdate: false });
    }
  }, [editor, conteudo, conteudoSeguro]);

  useEffect(() => {
    if (editor) editor.setEditable(!readOnly);
  }, [editor, readOnly]);

  return (
    <div
      ref={paperRef}
      className="caderno-editor-paper"
      style={{ zoom: `${zoom}%` }}
    >
      <EditorContent editor={editor} />
    </div>
  );
});

export default EditorTiptap;
