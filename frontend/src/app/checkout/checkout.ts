import { Component, inject, OnInit, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { DeliveryArea, DeliverySlot } from '../models/shop';
import { Api } from '../services/api';
import { Auth } from '../services/auth';
import { CartService } from '../services/cart';
import { Toast } from '../services/toast';
import { Icon } from '../shared/icon/icon';
import { loadDeliveryPref, manilaTodayIso, num, peso } from '../utils/format';

@Component({
  selector: 'app-checkout',
  imports: [ReactiveFormsModule, RouterLink, Icon],
  templateUrl: './checkout.html',
  styleUrl: './checkout.scss',
})
export class Checkout implements OnInit {
  private readonly api = inject(Api);
  private readonly fb = inject(FormBuilder);
  private readonly router = inject(Router);
  private readonly toast = inject(Toast);
  readonly auth = inject(Auth);
  readonly cart = inject(CartService);

  readonly areas = signal<DeliveryArea[]>([]);
  readonly slots = signal<DeliverySlot[]>([]);
  readonly step = signal<'delivery' | 'payment'>('delivery');
  readonly payment = signal('cod');
  readonly promo = signal('');
  readonly promoError = signal('');
  readonly submitting = signal(false);
  readonly peso = peso;
  readonly today = manilaTodayIso();

  readonly form = this.fb.nonNullable.group({
    recipient_name: ['', Validators.required],
    recipient_phone: ['', [Validators.required, Validators.minLength(7)]],
    address: ['', Validators.required],
    area_id: ['', Validators.required],
    delivery_date: [this.today, Validators.required],
    slot_id: ['', Validators.required],
    gift_message: [''],
    anonymous: [false],
    guest_email: [''],
    sender_name: [''],
  });

  ngOnInit() {
    this.api.areas().subscribe((rows) => this.areas.set(rows));
    this.api.slots().subscribe((rows) => {
      this.slots.set(rows);
      const saved = loadDeliveryPref();
      const match = saved && rows.some((row) => row.id === saved.slotId);
      if (saved?.date) {
        this.form.patchValue({
          delivery_date: saved.date,
          slot_id: match ? String(saved.slotId) : String(rows[0]?.id || ''),
        });
      } else if (rows[0]) {
        this.form.patchValue({ slot_id: String(rows[0].id) });
      }
    });
    const user = this.auth.user();
    if (user) {
      this.form.patchValue({ sender_name: user.first_name, guest_email: user.email });
    }
  }

  selectedArea() {
    return this.areas().find((area) => String(area.id) === this.form.controls.area_id.value);
  }

  deliveryFee() {
    return num(this.selectedArea()?.fee || 0);
  }

  total() {
    return Math.max(0, num(this.cart.cart().subtotal) + this.deliveryFee() - num(this.cart.cart().discount));
  }

  applyPromo() {
    this.promoError.set('');
    this.cart.applyPromo(this.promo(), (message) => this.promoError.set(message));
  }

  goPayment() {
    if (!this.auth.isLoggedIn() && !this.form.controls.guest_email.value) {
      this.form.controls.guest_email.setErrors({ required: true });
    }
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.toast.show('Please fill in the delivery details.', 'error');
      return;
    }
    this.step.set('payment');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  placeOrder() {
    if (this.submitting() || !this.cart.cart().items.length) {
      return;
    }
    this.submitting.set(true);
    const value = this.form.getRawValue();
    this.api
      .placeOrder({
        recipient_name: value.recipient_name,
        recipient_phone: value.recipient_phone,
        address: value.address,
        area_id: Number(value.area_id),
        delivery_date: value.delivery_date,
        slot_id: Number(value.slot_id),
        gift_message: value.gift_message || null,
        anonymous: value.anonymous,
        sender_name: value.sender_name || null,
        guest_email: this.auth.isLoggedIn() ? null : value.guest_email,
        payment_method: this.payment(),
      })
      .subscribe({
        next: (order) => {
          this.cart.refresh();
          this.router.navigate(['/order', order.order_number]);
        },
        error: (err) => {
          this.submitting.set(false);
          this.toast.show(err.error?.detail || 'Could not place the order.', 'error');
        },
      });
  }

  invalid(name: keyof typeof this.form.controls) {
    const control = this.form.controls[name];
    return control.invalid && control.touched;
  }

  setSlot(id: number) {
    this.form.patchValue({ slot_id: String(id) });
  }

  isSlot(id: number) {
    return this.form.controls.slot_id.value === String(id);
  }
}
