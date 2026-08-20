import { Component, computed, input } from '@angular/core';

export interface Testimonial {
  text: string;
  image: string;
  name: string;
  role: string;
}

@Component({
  selector: 'app-testimonials-column',
  templateUrl: './testimonials-column.html',
  styleUrl: './testimonials-column.scss',
  host: {
    '[class.col-tablet]': 'variant() === "tablet"',
    '[class.col-desktop]': 'variant() === "desktop"',
  },
})
export class TestimonialsColumn {
  readonly testimonials = input.required<Testimonial[]>();
  readonly duration = input(10);
  readonly variant = input<'default' | 'tablet' | 'desktop'>('default');
  readonly looped = computed(() => [...this.testimonials(), ...this.testimonials()]);
}
