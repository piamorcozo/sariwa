import { Component, inject, OnInit, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { DeliveryArea } from '../models/shop';
import { Api } from '../services/api';
import { Toast } from '../services/toast';
import { Icon } from '../shared/icon/icon';
import { peso } from '../utils/format';

@Component({
  selector: 'app-contact',
  imports: [ReactiveFormsModule, Icon],
  templateUrl: './contact.html',
  styleUrl: './contact.scss',
})
export class Contact implements OnInit {
  private readonly api = inject(Api);
  private readonly fb = inject(FormBuilder);
  private readonly toast = inject(Toast);
  readonly areas = signal<DeliveryArea[]>([]);
  readonly sent = signal(false);
  readonly peso = peso;
  readonly form = this.fb.nonNullable.group({
    name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    phone: [''],
    topic: ['order', Validators.required],
    message: ['', [Validators.required, Validators.minLength(8)]],
  });

  ngOnInit() {
    this.api.areas().subscribe((rows) => this.areas.set(rows));
  }

  submit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.api.contact(this.form.getRawValue()).subscribe({
      next: (res) => {
        this.sent.set(true);
        this.toast.show(res.message);
        this.form.reset({ topic: 'order' });
      },
      error: () => this.toast.show('Could not send that just now.', 'error'),
    });
  }
}
