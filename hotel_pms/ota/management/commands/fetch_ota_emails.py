"""
Management command to fetch OTA emails from Gmail and parse them.
Run: python manage.py fetch_ota_emails
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from imap_tools import MailBox, AND
from ota.service import OtaParsingService
from ota.schemas import OtaEmailIngestRequest
from ota.models import OtaEmail


class Command(BaseCommand):
    help = 'Fetches unread OTA emails from Gmail and parses them'

    def handle(self, *args, **options):
        if not settings.GMAIL_ADDRESS or not settings.GMAIL_APP_PASSWORD:
            self.stdout.write(self.style.ERROR('Gmail credentials not set in .env'))
            return

        self.stdout.write(f'Connecting to Gmail as {settings.GMAIL_ADDRESS}...')

        service = OtaParsingService()
        processed = 0
        skipped = 0
        failed = 0

        with MailBox('imap.gmail.com').login(settings.GMAIL_ADDRESS, settings.GMAIL_APP_PASSWORD, 'INBOX') as mailbox:
            for msg in mailbox.fetch(AND(seen=False), limit=100, mark_seen=True, reverse=True):
                if OtaEmail.objects.filter(raw_content__contains=msg.uid).exists():
                    skipped += 1
                    continue

                try:
                    email_request = OtaEmailIngestRequest(
                        sender_email=msg.from_,
                        subject=msg.subject,
                        raw_content=f"UID: {msg.uid}\nFrom: {msg.from_}\nSubject: {msg.subject}\n\n{msg.text or msg.html}",
                    )

                    try:
                        source, email_type, parser = service.resolve_parser(email_request)
                        result = parser.parse(email_request)

                        OtaEmail.objects.create(
                            source_channel=source,
                            subject=msg.subject,
                            sender_email=msg.from_,
                            raw_content=email_request.raw_content,
                            parsed_payload=result.model_dump(mode='json'),
                            processing_status='parsed',
                        )
                        self.stdout.write(self.style.SUCCESS(f'Parsed: {result.guest_name} from {source}'))
                        processed += 1
                    except Exception as parse_error:
                        self.stdout.write(self.style.WARNING(f'Failed: {msg.subject} -- {parse_error}'))
                        failed += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error: {e}'))
                    failed += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Done! Processed: {processed}, Skipped: {skipped}, Failed: {failed}'))
