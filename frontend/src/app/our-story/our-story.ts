import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { RollingCounter } from '../shared/counter/counter';
import { DriftWall } from '../shared/drift-wall/drift-wall';
import { DriftTile } from '../shared/drift-wall/drift-wall.models';

const photo = (id: string) =>
  `https://images.unsplash.com/${id}?auto=format&fit=crop&w=700&h=460&q=80`;

const CUSTOMERS: DriftTile[] = [
  { image: photo('photo-1522673607200-164d1b6ce486'), title: 'A quiet yes, Makati' },
  // { image: photo('photo-1455659817273-f96807779a8d'), title: 'Birthday morning, QC' },
  { image: photo('photo-1529636798458-92182e662485'), title: 'Just because, Pasig' },
  { image: photo('photo-1518199266791-5375a83190b7'), title: 'Roses at the door' },
  { image: photo('photo-1543168256-418811576931'), title: 'She knew before the note' },
  { image: photo('photo-1462275646964-a0e3386b89fa'), title: 'Sunday delivery, Taguig' },
  { image: photo('photo-1591886960571-74d43a9d4166'), title: 'Same-day surprise' },
  { image: photo('photo-1606041008023-472dfb5e530f'), title: 'Held like it mattered' },
  // { image: photo('photo-1487070181110-cdf2a6c4c044'), title: 'Hand-tied that morning' },
  { image: photo('photo-1563241527-3004b7be0ffd'), title: 'Color without a speech' },
  // { image: photo('photo-1526045478516-9914599705de'), title: 'White roses, no fuss' },
  // { image: photo('photo-1490750967868-88aa4da6ea27'), title: 'Tulips for a Tuesday' },
  { image: photo('photo-1487530811176-3780de880c2d'), title: 'A mixed garden gather' },
  // { image: photo('photo-1513279922550-26043555d41c'), title: 'The second the door opened' },
  // { image: photo('photo-1470506025382-cd125ba2c0a3'), title: 'Smile first, then the flowers' },
  { image: photo('photo-1530103862676-de8c9debad1d'), title: 'The party started early' },
  { image: photo('photo-1519741497674-611481863552'), title: 'Walked in with blooms' },
  // { image: photo('photo-1441123284222-18905b8b0bba'), title: 'A handful of summer' },
];

const FLOWERS_DELIVERED = 2500;

@Component({
  selector: 'app-our-story',
  imports: [RouterLink, DriftWall, RollingCounter],
  templateUrl: './our-story.html',
  styleUrl: './our-story.scss',
})
export class OurStory {
  readonly customers = CUSTOMERS;
  readonly flowers = FLOWERS_DELIVERED;
  readonly places = [1000, 100, 10, 1];
}
