import { Routes } from '@angular/router';
import { Home } from './home/home';
import { Shop } from './shop/shop';
import { ProductDetails } from './product-details/product-details';
import { Cart } from './cart/cart';
import { Checkout } from './checkout/checkout';
import { OrderConfirmation } from './order-confirmation/order-confirmation';
import { TrackOrder } from './track-order/track-order';
import { OurStory } from './our-story/our-story';
import { Contact } from './contact/contact';
import { Login } from './login/login';
import { Register } from './register/register';
import { Account } from './account/account';

export const routes: Routes = [
  { path: '', component: Home, title: 'Sariwa — Flowers, without the overthinking' },
  { path: 'shop', component: Shop, title: 'Shop — Sariwa' },
  { path: 'product/:slug', component: ProductDetails, title: 'Arrangement — Sariwa' },
  { path: 'cart', component: Cart, title: 'Your cart — Sariwa' },
  { path: 'checkout', component: Checkout, title: 'Checkout — Sariwa' },
  { path: 'order/:orderNumber', component: OrderConfirmation, title: 'Order — Sariwa' },
  { path: 'track', component: TrackOrder, title: 'Track an order — Sariwa' },
  { path: 'our-story', component: OurStory, title: 'Our story — Sariwa' },
  { path: 'contact', component: Contact, title: 'Contact — Sariwa' },
  { path: 'login', component: Login, title: 'Sign in — Sariwa' },
  { path: 'register', component: Register, title: 'Create account — Sariwa' },
  { path: 'account', component: Account, title: 'Account — Sariwa' },
  { path: '**', redirectTo: '' },
];
