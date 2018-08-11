# nvim_diary_template

Test repo for a plugin to generate a suitable template for VimWiki (for me).
This was mainly made to let me mess with various Python features, like the
NeoVim API, pipenv, mypy and more, there is a million and one simpler ways to
achieve this.

## Features:
- Google Calendar Integration:
    - Make a Diary entry, and have it auto-populated with todays events
      from GCal.
    - Any new events that are added, can be synced to GCal.
    - **TODO**: Add rename and remove syntax, such that events can be removed
      or edited.
- GitHub Issues Integration:
    - Use a Private repo on GitHub as an issue tracker, synced with your text
      diary. This is useful for ToDos, as well as keeping logs of how the todos
      are progressing.
    - Issues you make online and in-diary are synced, along with all
      comments.
    - Support for Github labels (including Deoplete source), including sorting
      by labels (needs config adding for this, currently a set sort order).
- Diary outline generation:
    - Builds a diary file with metadata in and the defined headings.

## Screenshot:

![The basic setup with GitHub and GCal integration](./docs/screenshot.png)

## Config:

Install with `vim-plug` like so, as well as ensuring the python env used with
Neovim has the required packages.

```viml
    Plug 'CrossR/nvim_diary_template', { 'do': ':UpdateRemotePlugins' }
```

#Basics:

Setup in your `init.vim` the following, for the location of the notes
and the location of the config.

```viml
    let g:nvim_diary_template#notes_path = "some/path/wiki/docs/"
    let g:nvim_diary_template#config_path = "some/path/wiki/config/"
```

Google Calendar and GitHub integration need a bit of manual work to get them
setup, which is as follows:

### GitHub

Generate an access token at Settings > Developer Settings > Personal access
tokens. Put this generated token in your config folder, in a json file called
`github_credentials.json` with the structure:

```json
    {"access_token": "XXX"}
```

Once this is added, add the following to your `init.vim`, to tell the plugin
where your GitHub repo is:

```viml
   let g:nvim_diary_template#repo_name = 'CrossR/nvim_diary_template'
```

### Google

This requires a few things, so an included `generate_google_credentials.py` file
is included.

TODO: Add instructions.
