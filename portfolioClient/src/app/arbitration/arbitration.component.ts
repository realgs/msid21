import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { CookieService } from 'ngx-cookie';
import { Observable } from 'rxjs';
import { ApiResult } from '../models/apiResult';
import { ResourceArbitration } from '../models/resourceStats';
import { PortfolioService } from '../portfolio.service';

@Component({
  selector: 'app-arbitration',
  templateUrl: './arbitration.component.html',
  styleUrls: ['./arbitration.component.css']
})
export class ArbitrationComponent implements OnInit {
  login?: string;
  selectedResource = new FormControl('all');
  arbitrations: ResourceArbitration[] = [];
  resources: string[] = [];
  status: string = 'ok';

  constructor(private service: PortfolioService, private cookie: CookieService) { }

  ngOnInit(): void {
    this.login = this.cookie.get('portfolioLogin');
    if (this.login){
      this.service.getResources(this.login)
      .subscribe(apiResult => {
        if (apiResult.success){
          for (let i = 0; i < apiResult.data.length; i++){
            this.resources.push(apiResult.data[i].name);
          }
        }
      })
      this.retrieveArbitrations();
    }
  }

  search(): void{
    this.retrieveArbitrations();
  }

  retrieveArbitrations(): void{
    if (this.login) {
      this.status = 'prending';
      let result: Observable<ApiResult>;
      const resource = this.selectedResource.value;
      if (resource != 'all'){
        result = this.service.getArbitrations(this.login, resource);
      }
      else{
        result = this.service.getArbitrations(this.login)
      }
      result.subscribe(apiResult => {
        if (apiResult.success){
          this.status = 'ok';
          this.arbitrations = apiResult.data;
        } else {
          this.status = 'error';
        }
      })
    }
  }

}
