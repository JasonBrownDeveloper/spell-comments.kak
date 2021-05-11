# spell-comments.kak

**spell-comments.kak** is a plugin for the [Kakoune](https://github.com/mawww/kakoune) editor.
It expands the included **spell** plugin to spell check only comments for languages supported by libclang.
This plugin uses python with the libclang module in addtion to aspell used by the **spell** plugin.

Additional arguments can be passed by overriding the `spellcommentscmd` option.
```
declare-option str spellcommentscmd %sh{
    printf '%s' "$(dirname $kak_source)/spell-comments.py -w"
}
```

Automatic spell checking can be done with a `hook`
```
hook global WinSetOption filetype=c %{
    hook window NormalIdle .* spell-comments
}
```
