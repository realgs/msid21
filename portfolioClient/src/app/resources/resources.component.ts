import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { CookieService } from 'ngx-cookie';
import { PortfolioService } from '../portfolio.service';
import { Resource } from '../models/resource';

@Component({
  selector: 'app-resources',
  templateUrl: './resources.component.html',
  styleUrls: ['./resources.component.css']
})
export class ResourcesComponent implements OnInit {
  private login?: string;
  resources: Resource[] = [];
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
        if (apiResult.success){
          const retrieved: Resource[] = [];
          for (let i = 0; i < apiResult.data.resources.length; i++){
            const res = apiResult.data.resources[i];
            retrieved.push({name: res.name, amount: res.amount, meanPurchase: res.meanPurchase});
          }
          this.resources = retrieved;
          this.currency = apiResult.data.currency;
        }
      })
    }
  }

  addResource(): void {
    if (this.login){
      let name = this.selectedResource.value;
      if (name == 'new') {
        name = this.name;
      }
      this.service.addResource(this.login, name, this.amount, this.price)
      .subscribe(apiResult => {
        if (apiResult.success){
          this.retrieveResources();
        }
      });
      this.clear();
    }
  }

  removeResource(): void {
    if (this.login){
      let name = this.selectedResource.value;
      if (name != 'new'){
        this.service.removeResource(this.login, name, this.amount)
        .subscribe(apiResult => {
          if (apiResult.success){
            this.retrieveResources();
          }
        });
        this.clear();
      }
    }
  }

  setAllAmount(): void {
    const resourceName = this.selectedResource.value;
    if (resourceName != 'new') {
      const resource = this.getResourceByName(resourceName);
      if (resource){
        this.amount = resource.amount;
      }
    }
  }

  private getResourceByName(name: string): Resource | undefined {
    for (let i = 0; i < this.resources.length; i++) {
      if (this.resources[i].name == name){
        return this.resources[i];
      }
    }
    return undefined;
  }

  private clear(): void{
    this.name = '';
    this.amount = 0;
    this.price = 0;
  }

}
