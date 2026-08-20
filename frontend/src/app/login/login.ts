import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Api } from '../services/api';
import { Auth } from '../services/auth';
import { Toast } from '../services/toast';
import { Icon } from '../shared/icon/icon';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, RouterLink, Icon],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  private readonly api = inject(Api);
  private readonly auth = inject(Auth);
  private readonly fb = inject(FormBuilder);
  private readonly router = inject(Router);
  private readonly toast = inject(Toast);
  readonly form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
  });

  submit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.api.login(this.form.getRawValue()).subscribe({
      next: (res) => {
        this.auth.setSession(res.access_token, res.user);
        this.router.navigateByUrl('/account');
      },
      error: (err) => this.toast.show(err.error?.detail || 'Could not sign in.', 'error'),
    });
  }
}
