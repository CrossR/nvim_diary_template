# nvim_diary_template

Test repo for a plugin to generate a suitable template for VimWiki (for me).
This was mainly made to let me mess with the NeoVim API with Python, there is a
million and one simpler ways to achieve this.

Features:
    - Google Calendar Integration:
        - Make a Diary entry, and have it auto-populated with todays events
          from GCal.
        - Any new events that are added, can be synced to GCal.
        - TODO: Add rename and remove syntax, such that events can be removed
          or edited.
    - ToDo roll-overs:
        - That is, for every uncompleted todo in the past N files, add them to
          the current diary entry.
        - TODO: Update to support `.` and `o` syntax, as currently it is just
          blank or checked.
    - Diary outline generation:
        - Builds a diary file with metadata in and the defined headings.
