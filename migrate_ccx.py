from ccx_keys.locator import CCXLocator
from notesapi.v1.models import Note

def get_key_without_branch(ccx_id):
    return str(CCXLocator.from_string(ccx_id).for_branch(None))


def migrate_ccx_keys(dry_run=False):
    damaged_notes = Note.objects.filter(course_id__contains="branch")

    notes_to_update = []
    for damaged_note in damaged_notes:
        versioned_course_id = damaged_note.course_id
        damaged_note.course_id = get_key_without_branch(versioned_course_id)
        notes_to_update.append(damaged_note)

    if dry_run:
        print(f'Dry run: Changes that would be made')
        print(f'Dry run: entries from {notes_to_update[0].id} to {notes_to_update[-1].id}')
    else:
        Note.objects.bulk_update(notes_to_update, ['course_id'], batch_size=500)
