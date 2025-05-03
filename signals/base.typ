#let conf(
  title: none,
  authors: (),
  abstract: [],
  doc,
) = {

set text(
  font: "New Computer Modern",
  size: 6pt
)
set page(
  paper: "a4",
  margin: (x: 1.8cm, y: 1.5cm),
)
set par(
  justify: true,
  leading: 0.52em,
)
set heading(numbering: "1.")
set math.equation(numbering: "(1)", supplement: [式])
columns(1, doc)
}