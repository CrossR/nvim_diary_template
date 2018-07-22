# nvim_diary_template

Test repo for a plugin to generate a suitable template for VimWiki (for me).
This was mainly made to let me mess with the NeoVim API with Python, there is a
million and one simpler ways to achieve this.

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
    - **TODO**: Add tags for projects, as well as the associated filtering.
- Diary outline generation:
    - Builds a diary file with metadata in and the defined headings.
