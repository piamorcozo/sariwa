import { Component } from '@angular/core';
import { Testimonial, TestimonialsColumn } from './testimonials-column';

const TESTIMONIALS: Testimonial[] = [
  {
    text: 'Ordered five minutes before a meeting. It still arrived same day, no drama.',
    image: 'https://randomuser.me/api/portraits/women/44.jpg',
    name: 'Regina',
    role: 'Makati',
  },
  {
    text: "I didn't have to scroll through a hundred bouquets to find one that made sense.",
    image: 'https://randomuser.me/api/portraits/men/32.jpg',
    name: 'Marco',
    role: 'Quezon City',
  },
  {
    text: 'Felt like asking a friend who knows flowers, not a website.',
    image: 'https://randomuser.me/api/portraits/women/68.jpg',
    name: 'Anna',
    role: 'Pasig',
  },
  {
    text: 'The handwritten note and fresh roses made it feel personal — not like a generic delivery.',
    image: 'https://randomuser.me/api/portraits/women/26.jpg',
    name: 'Camille',
    role: 'Taguig',
  },
  {
    text: 'Same-day delivery actually meant same day. It showed up before dinner, exactly as pictured.',
    image: 'https://randomuser.me/api/portraits/men/75.jpg',
    name: 'Javier',
    role: 'Mandaluyong',
  },
  {
    text: 'I picked a moment, chose from three great options, and checked out in under two minutes.',
    image: 'https://randomuser.me/api/portraits/women/90.jpg',
    name: 'Bianca',
    role: 'San Juan',
  },
  {
    text: 'The bouquet looked even better in person. My mom thought I had a florist on speed dial.',
    image: 'https://randomuser.me/api/portraits/men/52.jpg',
    name: 'Ethan',
    role: 'Parañaque',
  },
  {
    text: 'Tracking was clear, delivery was on time, and the flowers lasted a full week on the table.',
    image: 'https://randomuser.me/api/portraits/women/33.jpg',
    name: 'Lea',
    role: 'BGC',
  },
  {
    text: 'Finally a flower site that does not overwhelm you. Simple choices, beautiful results.',
    image: 'https://randomuser.me/api/portraits/men/41.jpg',
    name: 'Noah',
    role: 'Marikina',
  },
];

@Component({
  selector: 'app-testimonials',
  imports: [TestimonialsColumn],
  templateUrl: './testimonials.html',
  styleUrl: './testimonials.scss',
})
export class Testimonials {
  readonly firstColumn = TESTIMONIALS.slice(0, 3);
  readonly secondColumn = TESTIMONIALS.slice(3, 6);
  readonly thirdColumn = TESTIMONIALS.slice(6, 9);
}
