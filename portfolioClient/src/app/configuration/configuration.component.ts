import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { CookieService } from 'ngx-cookie';
import { ApiResult } from '../models/apiResult';
import { PortfolioService } from '../portfolio.service';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css']
})
export class ConfigurationComponent implements OnInit {
  private login?: string;
  fee?: number;
  currency?: FormControl;
  status: string = 'ok';

  constructor(private service: PortfolioService, private cookie: CookieService) { }

  ngOnInit(): void {
    this.login = this.cookie.get('portfolioLogin');
    if (this.login){
      this.service.getConfiguration(this.login)
      .subscribe(apiResult => this.retrieveConfiguration(apiResult))
    }
  }

  retrieveConfiguration(apiResult: ApiResult): void{
    if (apiResult.success){
      this.currency = new FormControl(apiResult.data.currency);
      this.fee = apiResult.data.fee;
    } else {
      this.status = 'notLoaded';
    }
  }

  save(): void{
    if (this.login && this.fee && this.currency) {
      this.status = 'pending'
      this.service.setConfiguration(this.login, this.currency.value, this.fee)
      .subscribe(apiResult => {
        if (apiResult.success) {
          this.status = 'saved';
        } else {
          this.status = 'error';
        }
      })
    }
  }

}
