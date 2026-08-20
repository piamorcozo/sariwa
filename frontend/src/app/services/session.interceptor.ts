import { HttpInterceptorFn } from '@angular/common/http';
import { sessionId } from '../utils/format';

export const sessionInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('sariwa_token');
  let headers = req.headers.set('X-Session-Id', sessionId());
  if (token) {
    headers = headers.set('Authorization', `Bearer ${token}`);
  }
  return next(req.clone({ headers }));
};
