import { Component, OnInit } from '@angular/core';
import { CookieService } from 'ngx-cookie';
import { PortfolioService } from '../portfolio.service';

@Component({
  selector: 'app-profit',
  templateUrl: './profit.component.html',
  styleUrls: ['./profit.component.css']
})
export class ProfitComponent implements OnInit {
  private login?: string;
  part: number = 10;
  newPart: number = 10;
  profits: any[] = [];

  constructor(private service: PortfolioService, private cookie: CookieService) { }

  ngOnInit(): void {
    this.login = this.cookie.get('portfolioLogin');
    this.retriveProfit();
  }

  retriveProfit(): void {
    if (this.login){
      let part = this.newPart;
      if (part > 100){
        part = 100;
      }
      this.service.getProfits(this.login, part)
      .subscribe(apiResult => {
        if (apiResult.success){
          this.profits = apiResult.data;
          this.part = part;
        }
      })
    }
  }
}
