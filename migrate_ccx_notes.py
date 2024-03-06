# myapp/management/commands/migrate_ccx_keys.py
from django.core.management.base import BaseCommand
from ccx_keys.locator import CCXLocator
from notesapi.v1.models import Note

class Command(BaseCommand):
    help = 'Migrate CCX keys in notes.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without making changes.')

    def handle(self, *args, **options):
        self.migrate_ccx_keys(dry_run=options['dry_run'])

    def get_key_without_branch(self, ccx_id):
        return str(CCXLocator.from_string(ccx_id).for_branch(None))

    def migrate_ccx_keys(self, dry_run=False):
        damaged_notes = Note.objects.filter(course_id__contains="branch")

        notes_to_update = []
        for damaged_note in damaged_notes:
            versioned_course_id = damaged_note.course_id
            damaged_note.course_id = self.get_key_without_branch(versioned_course_id)
            notes_to_update.append(damaged_note)

        if dry_run and notes_to_update:
            self.stdout.write('Dry run: Changes that would be made')
            self.stdout.write(f'Dry run: entries from {notes_to_update[0].id} to {notes_to_update[-1].id}')
        elif notes_to_update:
            Note.objects.bulk_update(notes_to_update, ['course_id'], batch_size=500)
