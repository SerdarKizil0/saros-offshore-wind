--[[
Pandoc Lua filter for the master manuscript (scripts/10_build_docx.py).

  * A Div with class "equation" and attribute number=N, holding one display
    equation, becomes a one-row, three-column layout table:
        [ marker | the equation (native OMML) | (N) ]
    The number carries the bookmark "eqN", so text links [Eq. N](#eqN)
    resolve inside Word and in the exported PDF. The marker text lets the
    post-processor find these tables, remove their borders and drop the
    marker; nothing else depends on it.
  * A Div with class "pagebreak" becomes a Word page break.
]]

local MARKER = "EQNLAYOUTTABLE"

local function cell(blocks, align)
  return pandoc.Cell(blocks, align or "AlignDefault", 1, 1)
end

function Div(el)
  if el.classes:includes("equation") then
    local n = el.attributes["number"]
    local number = pandoc.Plain({ pandoc.Span({ pandoc.Str("(" .. n .. ")") }, pandoc.Attr("eq" .. n)) })
    local row = pandoc.Row({
      cell({ pandoc.Plain({ pandoc.Str(MARKER) }) }, "AlignLeft"),
      cell(el.content, "AlignCenter"),
      cell({ number }, "AlignRight"),
    })
    local colspecs = { { "AlignLeft", 0.08 }, { "AlignCenter", 0.84 }, { "AlignRight", 0.08 } }
    local body = { attr = pandoc.Attr(), body = { row }, head = {}, row_head_columns = 0 }
    return pandoc.Table({ long = {} }, colspecs, pandoc.TableHead({}), { body }, pandoc.TableFoot({}))
  end
  if el.classes:includes("pagebreak") then
    return pandoc.RawBlock("openxml", '<w:p><w:pPr><w:suppressLineNumbers/></w:pPr><w:r><w:br w:type="page"/></w:r></w:p>')
  end
end
