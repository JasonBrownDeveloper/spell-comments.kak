declare-option str spellcommentscmd %sh{
    printf '%s' "$(dirname $kak_source)/spell-comments.py"
}

define-command -override -params ..1 -docstring %{
    spell-comments [<language>]: spell check the current buffer's comments

    The first optional argument is the language against which the check will be performed (overrides `spell_lang`)
    Formats of language supported:
      - ISO language code, e.g. 'en'
      - language code above followed by a dash or underscore with an ISO country code, e.g. 'en-US'
    } spell-comments %{
    try %{ add-highlighter window/ ranges 'spell_regions' }
    evaluate-commands %sh{
        file=$(mktemp -d "${TMPDIR:-/tmp}"/kak-spell.XXXXXXXX)/buffer
        printf 'eval -no-hooks write -sync %s\n' "${file}"
        printf 'set-option buffer spell_tmp_file %s\n' "${file}"
    }
    evaluate-commands %sh{
        use_lang() {
            if ! printf %s "$1" | grep -qE '^[a-z]{2,3}([_-][A-Z]{2})?$'; then
                echo "fail 'Invalid language code (examples of expected format: en, en_US, en-US)'"
                rm -rf "$(dirname "$kak_opt_spell_tmp_file")"
                exit 1
            else
                options="-l '$1'"
                printf 'set-option buffer spell_last_lang %s\n' "$1"
            fi
        }

        if [ $# -ge 1 ]; then
            use_lang "$1"
        elif [ -n "${kak_opt_spell_lang}" ]; then
            use_lang "${kak_opt_spell_lang}"
        fi

        {
            printf "set-option buffer=$kak_bufname spell_regions $kak_timestamp %s\n" "$($kak_opt_spellcommentscmd $options "$kak_opt_spell_tmp_file")" | kak -p $kak_session
            rm -rf $(dirname "$kak_opt_spell_tmp_file")
        } </dev/null >/dev/null 2>&1 &
    }
}
