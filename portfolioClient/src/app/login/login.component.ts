import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { Router } from '@angular/router';
import { PortfolioService } from '../portfolio.service';
import { ApiResult } from '../models/apiResult';
import { CookieService } from 'ngx-cookie';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  login: string = '';
  status: string = 'ok';
  @Output() logged = new EventEmitter();

  constructor(private service: PortfolioService, private cookieService: CookieService) { }

  load(): void{
    this.status = 'pending';
    this.service.load(this.login)
    .subscribe(loadResult => this.afterLoad(loadResult, this.login));
  }

  afterLoad(loadResult: ApiResult, login: string): void{
    if (loadResult.success){
      this.status = 'ok';
      this.cookieService.put('portfolioLogin', login);
      this.logged.emit();
    }
    else{
      this.status = 'fail';
    }
  }

}
