import { Component, inject } from '@angular/core';
import { Toast as ToastService } from '../../services/toast';

@Component({
  selector: 'app-toast',
  templateUrl: './toast.html',
  styleUrl: './toast.scss',
})
export class Toast {
  readonly toast = inject(ToastService);
}
