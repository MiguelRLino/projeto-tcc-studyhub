import {
  AlignCenter,
  AlignJustify,
  AlignLeft,
  AlignRight,
  Bold,
  Code,
  Heading1,
  Heading2,
  Heading3,
  Highlighter,
  ImagePlus,
  IndentDecrease,
  IndentIncrease,
  Italic,
  Link2,
  List,
  ListChecks,
  ListOrdered,
  Maximize2,
  Minimize2,
  Minus,
  Palette,
  Quote,
  Redo2,
  RemoveFormatting,
  Strikethrough,
  Subscript,
  Superscript,
  Table2,
  Underline,
  Undo2,
  Unlink,
} from "lucide-react";

const FONTES = [
  { label: "Inter", value: "Inter, sans-serif" },
  { label: "Arial", value: "Arial, sans-serif" },
  { label: "Times New Roman", value: "'Times New Roman', serif" },
  { label: "Georgia", value: "Georgia, serif" },
  { label: "Verdana", value: "Verdana, sans-serif" },
  { label: "Calibri", value: "Calibri, sans-serif" },
  { label: "Courier New", value: "'Courier New', monospace" },
  { label: "Roboto", value: "Roboto, sans-serif" },
];

const TAMANHOS = ["8px", "10px", "11px", "12px", "14px", "16px", "18px", "20px", "24px", "28px", "32px", "36px", "48px", "72px"];

const CORES = ["#f9fafb", "#6366f1", "#3b82f6", "#22c55e", "#eab308", "#fb923c", "#ef4444", "#ec4899", "#a855f7"];

function Btn({ onClick, active, title, children, disabled }) {
  return (
    <button
      type="button"
      className={`caderno-toolbar-btn${active ? " is-active" : ""}`}
      onClick={onClick}
      title={title}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

export default function ToolbarEditor({
  editor,
  onInserirImagem,
  telaCheia,
  onToggleTelaCheia,
  zoom,
  onZoomChange,
}) {
  if (!editor) return null;

  function setLink() {
    const prev = editor.getAttributes("link").href;
    const url = window.prompt("URL do link:", prev || "https://");
    if (url === null) return;
    if (url === "") {
      editor.chain().focus().extendMarkRange("link").unsetLink().run();
      return;
    }
    editor.chain().focus().extendMarkRange("link").setLink({ href: url }).run();
  }

  function inserirTabela() {
    editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run();
  }

  return (
    <div className="caderno-toolbar">
      <div className="caderno-toolbar-group">
        <Btn onClick={() => editor.chain().focus().undo().run()} title="Desfazer">
          <Undo2 size={16} />
        </Btn>
        <Btn onClick={() => editor.chain().focus().redo().run()} title="Refazer">
          <Redo2 size={16} />
        </Btn>
      </div>

      <div className="caderno-toolbar-group">
        <select
          className="caderno-toolbar-select"
          value={editor.getAttributes("textStyle").fontFamily || ""}
          onChange={(e) =>
            editor.chain().focus().setFontFamily(e.target.value || null).run()
          }
          title="Fonte"
        >
          <option value="">Fonte</option>
          {FONTES.map((f) => (
            <option key={f.value} value={f.value}>
              {f.label}
            </option>
          ))}
        </select>
        <select
          className="caderno-toolbar-select caderno-toolbar-select--sm"
          value={editor.getAttributes("textStyle").fontSize || ""}
          onChange={(e) =>
            e.target.value
              ? editor.chain().focus().setFontSize(e.target.value).run()
              : editor.chain().focus().unsetFontSize().run()
          }
          title="Tamanho"
        >
          <option value="">Tam.</option>
          {TAMANHOS.map((t) => (
            <option key={t} value={t}>
              {t.replace("px", "")}
            </option>
          ))}
        </select>
      </div>

      <div className="caderno-toolbar-group">
        <Btn
          active={editor.isActive("bold")}
          onClick={() => editor.chain().focus().toggleBold().run()}
          title="Negrito"
        >
          <Bold size={16} />
        </Btn>
        <Btn
          active={editor.isActive("italic")}
          onClick={() => editor.chain().focus().toggleItalic().run()}
          title="Itálico"
        >
          <Italic size={16} />
        </Btn>
        <Btn
          active={editor.isActive("underline")}
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          title="Sublinhado"
        >
          <Underline size={16} />
        </Btn>
        <Btn
          active={editor.isActive("strike")}
          onClick={() => editor.chain().focus().toggleStrike().run()}
          title="Tachado"
        >
          <Strikethrough size={16} />
        </Btn>
        <Btn
          active={editor.isActive("superscript")}
          onClick={() => editor.chain().focus().toggleSuperscript().run()}
          title="Sobrescrito"
        >
          <Superscript size={16} />
        </Btn>
        <Btn
          active={editor.isActive("subscript")}
          onClick={() => editor.chain().focus().toggleSubscript().run()}
          title="Subscrito"
        >
          <Subscript size={16} />
        </Btn>
        <Btn
          onClick={() => editor.chain().focus().unsetAllMarks().clearNodes().run()}
          title="Limpar formatação"
        >
          <RemoveFormatting size={16} />
        </Btn>
      </div>

      <div className="caderno-toolbar-group caderno-toolbar-colors">
        <label className="caderno-toolbar-color" title="Cor do texto">
          <Palette size={14} />
          <input
            type="color"
            value={editor.getAttributes("textStyle").color || "#f9fafb"}
            onChange={(e) => editor.chain().focus().setColor(e.target.value).run()}
          />
        </label>
        <div className="caderno-toolbar-swatches">
          {CORES.map((c) => (
            <button
              key={c}
              type="button"
              className="caderno-swatch"
              style={{ background: c }}
              title={`Cor ${c}`}
              onClick={() => editor.chain().focus().setColor(c).run()}
            />
          ))}
        </div>
        <label className="caderno-toolbar-color" title="Destaque">
          <Highlighter size={14} />
          <input
            type="color"
            defaultValue="#6366f1"
            onChange={(e) =>
              editor.chain().focus().toggleHighlight({ color: e.target.value }).run()
            }
          />
        </label>
      </div>

      <div className="caderno-toolbar-group">
        <Btn
          active={editor.isActive("heading", { level: 1 })}
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          title="Título 1"
        >
          <Heading1 size={16} />
        </Btn>
        <Btn
          active={editor.isActive("heading", { level: 2 })}
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          title="Título 2"
        >
          <Heading2 size={16} />
        </Btn>
        <Btn
          active={editor.isActive("heading", { level: 3 })}
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          title="Título 3"
        >
          <Heading3 size={16} />
        </Btn>
      </div>

      <div className="caderno-toolbar-group">
        <Btn
          active={editor.isActive({ textAlign: "left" })}
          onClick={() => editor.chain().focus().setTextAlign("left").run()}
          title="Esquerda"
        >
          <AlignLeft size={16} />
        </Btn>
        <Btn
          active={editor.isActive({ textAlign: "center" })}
          onClick={() => editor.chain().focus().setTextAlign("center").run()}
          title="Centro"
        >
          <AlignCenter size={16} />
        </Btn>
        <Btn
          active={editor.isActive({ textAlign: "right" })}
          onClick={() => editor.chain().focus().setTextAlign("right").run()}
          title="Direita"
        >
          <AlignRight size={16} />
        </Btn>
        <Btn
          active={editor.isActive({ textAlign: "justify" })}
          onClick={() => editor.chain().focus().setTextAlign("justify").run()}
          title="Justificado"
        >
          <AlignJustify size={16} />
        </Btn>
      </div>

      <div className="caderno-toolbar-group">
        <Btn
          active={editor.isActive("bulletList")}
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          title="Lista"
        >
          <List size={16} />
        </Btn>
        <Btn
          active={editor.isActive("orderedList")}
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          title="Numeração"
        >
          <ListOrdered size={16} />
        </Btn>
        <Btn
          active={editor.isActive("taskList")}
          onClick={() => editor.chain().focus().toggleTaskList().run()}
          title="Checklist"
        >
          <ListChecks size={16} />
        </Btn>
        <Btn
          onClick={() => editor.chain().focus().sinkListItem("listItem").run()}
          title="Aumentar recuo"
        >
          <IndentIncrease size={16} />
        </Btn>
        <Btn
          onClick={() => editor.chain().focus().liftListItem("listItem").run()}
          title="Diminuir recuo"
        >
          <IndentDecrease size={16} />
        </Btn>
      </div>

      <div className="caderno-toolbar-group">
        <Btn
          active={editor.isActive("blockquote")}
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          title="Citação"
        >
          <Quote size={16} />
        </Btn>
        <Btn
          onClick={() => editor.chain().focus().setHorizontalRule().run()}
          title="Linha horizontal"
        >
          <Minus size={16} />
        </Btn>
        <Btn onClick={setLink} active={editor.isActive("link")} title="Link">
          <Link2 size={16} />
        </Btn>
        <Btn
          onClick={() => editor.chain().focus().unsetLink().run()}
          title="Remover link"
          disabled={!editor.isActive("link")}
        >
          <Unlink size={16} />
        </Btn>
        <Btn
          active={editor.isActive("code")}
          onClick={() => editor.chain().focus().toggleCode().run()}
          title="Código inline"
        >
          <Code size={16} />
        </Btn>
        <Btn
          active={editor.isActive("codeBlock")}
          onClick={() => editor.chain().focus().toggleCodeBlock().run()}
          title="Bloco de código"
        >
          <Code size={16} />
        </Btn>
        <Btn onClick={inserirTabela} title="Tabela">
          <Table2 size={16} />
        </Btn>
        {editor.can().addRowAfter?.() ? (
          <>
            <Btn onClick={() => editor.chain().focus().addRowAfter().run()} title="Linha +">
              +L
            </Btn>
            <Btn onClick={() => editor.chain().focus().addColumnAfter().run()} title="Coluna +">
              +C
            </Btn>
            <Btn onClick={() => editor.chain().focus().deleteRow().run()} title="Excluir linha">
              −L
            </Btn>
            <Btn onClick={() => editor.chain().focus().deleteColumn().run()} title="Excluir coluna">
              −C
            </Btn>
            <Btn onClick={() => editor.chain().focus().deleteTable().run()} title="Excluir tabela">
              ⊠
            </Btn>
          </>
        ) : null}
        <Btn onClick={onInserirImagem} title="Imagem">
          <ImagePlus size={16} />
        </Btn>
      </div>

      <div className="caderno-toolbar-group caderno-toolbar-group--end">
        <select
          className="caderno-toolbar-select caderno-toolbar-select--sm"
          value={zoom}
          onChange={(e) => onZoomChange(Number(e.target.value))}
          title="Zoom"
        >
          {[75, 90, 100, 110, 125, 150].map((z) => (
            <option key={z} value={z}>
              {z}%
            </option>
          ))}
        </select>
        <Btn onClick={onToggleTelaCheia} title={telaCheia ? "Sair tela cheia" : "Tela cheia"}>
          {telaCheia ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
        </Btn>
      </div>
    </div>
  );
}
