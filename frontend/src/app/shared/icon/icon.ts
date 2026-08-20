import { Component, computed, input } from '@angular/core';

const ALIASES: Record<string, string> = {
  heart: 'like',
  tulip: 'flower',
  'peace-symbol': 'dove',
  'credit-card': 'bank-cards',
  login: 'login-rounded-right',
  logout: 'logout-rounded-left',
};

@Component({
  selector: 'app-icon',
  templateUrl: './icon.html',
  styleUrl: './icon.scss',
})
export class Icon {
  readonly name = input.required<string>();
  readonly size = input(20);
  readonly label = input('');
  readonly invert = input(false);
  readonly src = computed(() => `icons/${ALIASES[this.name()] || this.name()}.png`);
}
