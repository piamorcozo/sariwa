import { Component, ElementRef, ViewChild, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ChatOption } from '../../models/shop';
import { Api } from '../../services/api';
import { Icon } from '../icon/icon';

interface ChatLine {
  role: 'bot' | 'user';
  text: string;
  time: string;
  link?: { url: string; label: string } | null;
  handover?: boolean;
  showOptions?: boolean;
}

@Component({
  selector: 'app-chatbot',
  imports: [FormsModule, RouterLink, Icon],
  templateUrl: './chatbot.html',
  styleUrl: './chatbot.scss',
})
export class Chatbot {
  private readonly api = inject(Api);

  @ViewChild('thread') private thread?: ElementRef<HTMLElement>;

  readonly open = signal(false);
  readonly language = signal<'en' | 'tl'>('en');
  readonly options = signal<ChatOption[]>([]);
  readonly messages = signal<ChatLine[]>([]);
  readonly typing = signal(false);
  readonly draft = signal('');
  readonly menuOpen = signal(false);

  constructor() {
    this.loadOptions();
  }

  toggle() {
    const next = !this.open();
    this.open.set(next);
    this.menuOpen.set(false);
    if (next && this.messages().length === 0) {
      this.startConversation();
    }
  }

  minimize() {
    this.open.set(false);
    this.menuOpen.set(false);
  }

  setLanguage(language: 'en' | 'tl') {
    if (this.language() === language) {
      return;
    }
    this.language.set(language);
    this.loadOptions();
    this.reset();
  }

  reset() {
    this.menuOpen.set(false);
    this.messages.set([]);
    this.draft.set('');
    this.typing.set(false);
    if (this.open()) {
      this.startConversation();
    }
  }

  send(text?: string, intent?: string) {
    const message = (text ?? this.draft()).trim();
    if (!message || this.typing()) {
      return;
    }
    this.draft.set('');
    this.push({ role: 'user', text: message, time: this.now() });
    this.typing.set(true);
    this.scrollSoon();

    this.api.askChat(message, this.language(), intent).subscribe({
      next: (res) => {
        window.setTimeout(() => {
          this.typing.set(false);
          this.push({
            role: 'bot',
            text: res.reply,
            time: this.now(),
            link: res.link,
            handover: res.handover,
            showOptions: res.show_options,
          });
          this.scrollSoon();
        }, 550);
      },
      error: () => {
        this.typing.set(false);
        this.push({
          role: 'bot',
          text:
            this.language() === 'tl'
              ? 'May sagabal sa linya. Subukan ulit, o i-email kami sa hello@sariwa.ph.'
              : 'Something went wrong on our side. Try again, or email hello@sariwa.ph.',
          time: this.now(),
        });
      },
    });
  }

  pick(option: ChatOption) {
    this.send(option.label, option.slug);
  }

  onSubmit(event: Event) {
    event.preventDefault();
    this.send();
  }

  private startConversation() {
    const tl = this.language() === 'tl';
    this.messages.set([
      {
        role: 'bot',
        text: tl
          ? 'Hi! Ako si Sariwa Bot, ang flower assistant ninyo. Paano kita matutulungan ngayon?'
          : "Hi there! I'm Sariwa Bot, your flower assistant. How can I help you today?",
        time: this.now(),
        showOptions: true,
      },
    ]);
    this.scrollSoon();
  }

  private loadOptions() {
    this.api.chatOptions(this.language()).subscribe((rows) => this.options.set(rows));
  }

  private push(line: ChatLine) {
    this.messages.update((rows) => [...rows, line]);
  }

  private now() {
    return new Date().toLocaleTimeString('en-PH', { hour: 'numeric', minute: '2-digit' });
  }

  private scrollSoon() {
    queueMicrotask(() => {
      const el = this.thread?.nativeElement;
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
    });
  }
}
