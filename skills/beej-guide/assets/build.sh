#!/usr/bin/env bash
# Build "BOOK_TITLE": PDF + split-per-chapter HTML.
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/usr/local/texlive/2025basic/bin/universal-darwin:$PATH"

CHAPTERS=(chapters/*.md)
OUT=out
HTML_DIR="$OUT/html"
PDF="$OUT/BOOK_SLUG.pdf"
HL=(--syntax-highlighting=tango)   # add --syntax-definition=LANG.xml if needed

mkdir -p "$HTML_DIR"

echo "== Building PDF =="
pandoc metadata.yaml "${CHAPTERS[@]}" \
    --from markdown \
    --pdf-engine=pdflatex \
    --top-level-division=chapter \
    --toc --number-sections \
    "${HL[@]}" \
    -o "$PDF"
echo "   -> $PDF"

echo "== Building split HTML =="
cp style.css "$HTML_DIR/"

# Collect page filenames and chapter titles (first level-1 heading per file).
pages=()
titles=()
for f in "${CHAPTERS[@]}"; do
    base=$(basename "$f" .md)
    pages+=("$base.html")
    titles+=("$(sed -n 's/^# //p' "$f" | head -1)")
done

n=${#CHAPTERS[@]}
for i in "${!CHAPTERS[@]}"; do
    f="${CHAPTERS[$i]}"
    page="${pages[$i]}"
    title="${titles[$i]}"

    prev='<span class="prev"></span>'
    next='<span class="next"></span>'
    if (( i > 0 )); then
        prev="<span class=\"prev\">&larr; <a href=\"${pages[$((i-1))]}\">${titles[$((i-1))]}</a></span>"
    fi
    if (( i < n - 1 )); then
        next="<span class=\"next\"><a href=\"${pages[$((i+1))]}\">${titles[$((i+1))]}</a> &rarr;</span>"
    fi
    home='<span class="home"><a href="index.html">Contents</a></span>'

    navtop=$(mktemp); navbot=$(mktemp)
    printf '<nav class="booknav top">%s%s%s</nav>\n' "$prev" "$home" "$next" > "$navtop"
    printf '<nav class="booknav bottom">%s%s%s</nav>\n' "$prev" "$home" "$next" > "$navbot"

    pandoc "$f" \
        --from markdown \
        --to html5 --standalone \
        --css style.css \
        --number-sections --number-offset="$i" \
        "${HL[@]}" \
        --metadata pagetitle="$title — BOOK_TITLE" \
        --include-before-body="$navtop" \
        --include-after-body="$navbot" \
        -o "$HTML_DIR/$page"
    rm -f "$navtop" "$navbot"
done

# Index page: cover + table of contents.
indexmd=$(mktemp)
{
    cat <<'COVER'
<div class="cover">
<div class="title">BOOK_TITLE</div>
<div class="subtitle">BOOK_SUBTITLE</div>
<div class="author">AUTHOR_NAME</div>
<div class="version">VERSION_AND_DATE</div>
</div>

## Contents

COVER
    echo '<ul class="toc">'
    for i in "${!pages[@]}"; do
        printf '<li>%d. <a href="%s">%s</a></li>\n' "$((i+1))" "${pages[$i]}" "${titles[$i]}"
    done
    echo '</ul>'
} > "$indexmd"

pandoc "$indexmd" \
    --from markdown \
    --to html5 --standalone \
    --css style.css \
    --metadata pagetitle="BOOK_TITLE" \
    -o "$HTML_DIR/index.html"
rm -f "$indexmd"

echo "   -> $HTML_DIR/index.html (+ ${n} chapter pages)"
echo "== Done =="
