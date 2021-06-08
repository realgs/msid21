import { Component, OnInit } from '@angular/core';
import { CookieService } from 'ngx-cookie';
import { PortfolioService } from '../portfolio.service';

@Component({
  selector: 'app-profit',
  templateUrl: './valueAndProfit.component.html',
  styleUrls: ['./valueAndProfit.component.css']
})
export class ValueAndProfitComponent implements OnInit {
  private login?: string;
  part: number = 10;
  newPart: number = 10;
  currency: string = 'USD';
  stats: any[] = [];
  status: string = 'ok';

  constructor(private service: PortfolioService, private cookie: CookieService) { }

  ngOnInit(): void {
    this.login = this.cookie.get('portfolioLogin');
    this.retriveData();
  }

  retriveData(): void {
    if (this.login){
      this.status = 'pending';
      let part = this.newPart;
      if (part > 100){
        part = 100;
      }
      this.service.getStats(this.login, part)
      .subscribe(apiResult => {
        if (apiResult.success){
          this.stats = apiResult.data.stats;
          this.currency = apiResult.data.currency;
          this.part = part;
          this.status = 'ok';
        } else {
          this.status = 'error';
        }
      });
    }
  }
}
