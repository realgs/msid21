import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { CookieService } from 'ngx-cookie';
import { PortfolioService } from '../portfolio.service';

@Component({
  selector: 'app-resources',
  templateUrl: './resources.component.html',
  styleUrls: ['./resources.component.css']
})
export class ResourcesComponent implements OnInit {
  private login?: string;
  resources: any[] = [];
  selectedResource = new FormControl('new');
  currency: string = 'USD';
  name: string = '';
  amount: number = 0;
  price: number = 0;

  constructor(private service: PortfolioService, private cookie: CookieService) { }

  ngOnInit(): void {
    this.login = this.cookie.get('portfolioLogin');
    this.retrieveResources();
  }

  retrieveResources(): void {
    if (this.login) {
      this.service.getResources(this.login)
      .subscribe(apiResult => {
        if (apiResult.success && apiResult.data.length){
          this.resources = apiResult.data;
          this.currency = apiResult.data[0].currency;
        }
      })
    }
  }

  addResource(): void {
    if (this.login){
      this.clear();
      this.service.addResource(this.login, this.name, this.amount, this.price)
      .subscribe(apiResult => {
        if (apiResult.success){
          this.retrieveResources();
        }
      })
    }
  }

  clear(): void{
    this.name = '';
    this.amount = 0;
    this.price = 0;
  }

}
