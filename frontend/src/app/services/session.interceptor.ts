import { HttpInterceptorFn } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { sessionId } from '../utils/format';

function apiBase(): string {
  if (environment.apiBase) {
    return environment.apiBase;
  }
  if (typeof window !== 'undefined' && window.location.hostname.endsWith('.onrender.com')) {
    return environment.hostedApiBase;
  }
  return '';
}

export const sessionInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('sariwa_token');
  let headers = req.headers.set('X-Session-Id', sessionId());
  if (token) {
    headers = headers.set('Authorization', `Bearer ${token}`);
  }
  let url = req.url;
  const base = apiBase();
  if (base && url.startsWith('/api')) {
    url = `${base.replace(/\/$/, '')}${url}`;
  }
  return next(req.clone({ url, headers }));
};
