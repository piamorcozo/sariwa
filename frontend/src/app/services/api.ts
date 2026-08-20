import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import {
  AuthResponse,
  Cart,
  DeliveryArea,
  DeliverySlot,
  FlowerType,
  Occasion,
  Order,
  ProductCard,
  ProductDetail,
  SameDay,
  User,
  ChatAsk,
  ChatOption,
} from '../models/shop';

@Injectable({ providedIn: 'root' })
export class Api {
  private readonly http = inject(HttpClient);

  occasions(): Observable<Occasion[]> {
    return this.http.get<Occasion[]>('/api/occasions');
  }

  flowerTypes(): Observable<FlowerType[]> {
    return this.http.get<FlowerType[]>('/api/flower-types');
  }

  areas(): Observable<DeliveryArea[]> {
    return this.http.get<DeliveryArea[]>('/api/delivery-areas');
  }

  slots(): Observable<DeliverySlot[]> {
    return this.http.get<DeliverySlot[]>('/api/delivery-slots');
  }

  sameDay(): Observable<SameDay> {
    return this.http.get<SameDay>('/api/same-day');
  }

  products(filters: Record<string, string | number | boolean | undefined> = {}): Observable<ProductCard[]> {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, String(value));
      }
    });
    return this.http.get<ProductCard[]>('/api/products', { params });
  }

  product(slug: string): Observable<ProductDetail> {
    return this.http.get<ProductDetail>(`/api/products/${slug}`);
  }

  similar(slug: string): Observable<ProductCard[]> {
    return this.http.get<ProductCard[]>(`/api/products/${slug}/similar`);
  }

  toggleFavorite(productId: number) {
    return this.http.post<{ favorited: boolean }>(`/api/products/${productId}/favorite`, {});
  }

  cart(): Observable<Cart> {
    return this.http.get<Cart>('/api/cart');
  }

  addToCart(productId: number, sizeId: number, quantity = 1): Observable<Cart> {
    return this.http.post<Cart>('/api/cart/items', {
      product_id: productId,
      size_id: sizeId,
      quantity,
    });
  }

  updateCartItem(itemId: number, quantity: number): Observable<Cart> {
    return this.http.patch<Cart>(`/api/cart/items/${itemId}`, { quantity });
  }

  removeCartItem(itemId: number): Observable<Cart> {
    return this.http.delete<Cart>(`/api/cart/items/${itemId}`);
  }

  applyPromo(code: string): Observable<Cart> {
    return this.http.post<Cart>('/api/cart/promo', { code });
  }

  placeOrder(payload: Record<string, unknown>): Observable<Order> {
    return this.http.post<Order>('/api/orders', payload);
  }

  order(orderNumber: string): Observable<Order> {
    return this.http.get<Order>(`/api/orders/${orderNumber}`);
  }

  myOrders(): Observable<Order[]> {
    return this.http.get<Order[]>('/api/orders');
  }

  register(payload: Record<string, string>): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/register', payload);
  }

  login(payload: Record<string, string>): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/login', payload);
  }

  me(): Observable<User> {
    return this.http.get<User>('/api/auth/me');
  }

  favorites(): Observable<ProductCard[]> {
    return this.http.get<ProductCard[]>('/api/auth/favorites');
  }

  contact(payload: Record<string, string>): Observable<{ ok: boolean; message: string }> {
    return this.http.post<{ ok: boolean; message: string }>('/api/contact', payload);
  }

  chatOptions(language: 'en' | 'tl' = 'en'): Observable<ChatOption[]> {
    return this.http.get<ChatOption[]>('/api/chat/options', { params: { language } });
  }

  askChat(message: string, language: 'en' | 'tl' = 'en', intent?: string): Observable<ChatAsk> {
    return this.http.post<ChatAsk>('/api/chat/ask', { message, language, intent: intent || null });
  }
}
