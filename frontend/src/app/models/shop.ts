export interface Occasion {
  id: number;
  slug: string;
  name: string;
  icon: string;
}

export interface FlowerType {
  id: number;
  slug: string;
  name: string;
}

export interface ProductSize {
  id: number;
  name: string;
  stem_count: number | null;
  price: number | string;
  compare_at_price: number | string | null;
  is_default: boolean;
}

export interface ProductImage {
  id: number;
  url: string;
  alt: string;
}

export interface Review {
  id: number;
  rating: number;
  comment: string;
  author: string;
  created_at: string;
}

export interface ProductCard {
  id: number;
  slug: string;
  name: string;
  short_description: string;
  featured: boolean;
  same_day_eligible: boolean;
  color_palette: string;
  default_size_id: number;
  price: number | string;
  compare_at_price: number | string | null;
  occasion: string | null;
  occasion_slugs: string[];
  flower_type: string;
  image: string | null;
  rating: number;
  review_count: number;
  favorited: boolean;
}

export interface ProductDetail extends ProductCard {
  description: string;
  included_text: string;
  delivery_text: string;
  care_text: string;
  sizes: ProductSize[];
  images: ProductImage[];
  occasions: Occasion[];
  reviews: Review[];
}

export interface DeliveryArea {
  id: number;
  slug: string;
  name: string;
  fee: number | string;
  is_core: boolean;
}

export interface DeliverySlot {
  id: number;
  slug: string;
  name: string;
  sort_order: number;
}

export interface CartItem {
  id: number;
  product_id: number;
  size_id: number;
  slug: string;
  name: string;
  size_name: string;
  short_description: string;
  image: string | null;
  color_palette: string;
  unit_price: number | string;
  quantity: number;
  line_total: number | string;
}

export interface Cart {
  id: number;
  items: CartItem[];
  subtotal: number | string;
  delivery_fee: number | string;
  discount: number | string;
  total: number | string;
  promo_code: string | null;
  promo_message: string | null;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  role: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface OrderItem {
  product_name: string;
  size_name: string;
  unit_price: number | string;
  quantity: number;
  image: string | null;
}

export interface Order {
  order_number: string;
  status: string;
  recipient_name: string;
  recipient_phone: string;
  address: string;
  area_name: string;
  delivery_date: string;
  slot_name: string;
  gift_message: string | null;
  anonymous: boolean;
  payment_method: string;
  payment_status: string;
  subtotal: number | string;
  delivery_fee: number | string;
  discount: number | string;
  total: number | string;
  created_at: string;
  items: OrderItem[];
}

export interface SameDay {
  eligible: boolean;
  cutoff: string;
  remaining_seconds: number;
  label: string;
}

export interface ChatOption {
  slug: string;
  icon: string;
  label: string;
}

export interface ChatAsk {
  reply: string;
  matched: boolean;
  language: string;
  handover: boolean;
  show_options: boolean;
  slug: string | null;
  link: { url: string; label: string } | null;
}
