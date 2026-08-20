export interface DriftTile {
  image: string;
  title?: string;
  href?: string;
}

export interface CounterPlace {
  kind: 'digit' | 'dot';
  value: number | '.';
}
