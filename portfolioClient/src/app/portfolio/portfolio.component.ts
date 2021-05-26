import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { PortfolioService } from '../portfolio.service';
import { ResourceStats } from  '../models/resourceStats';
import { MatDialog } from '@angular/material/dialog';
import { ResourceDetailsComponent } from '../resource-details/resource-details.component';
import { CookieService } from 'ngx-cookie';

@Component({
  selector: 'app-portfolio',
  templateUrl: './portfolio.component.html',
  styleUrls: ['./portfolio.component.css']
})
export class PortfolioComponent implements OnInit {
  stats: any = [];
  login: string = '';
  message: string = '';

  constructor(private service: PortfolioService, public dialog: MatDialog, private cookie: CookieService) { }

  ngOnInit(): void {
    const login = this.cookie.get('portfolioLogin');
    if (login) {
      this.login = login;
      this.retrieveStats();
    }
  }

  openDetails(resourceStats: ResourceStats): void{
    this.dialog.open(ResourceDetailsComponent, {data: resourceStats});
  }

  private retrieveStats(part?: number): void{
    this.service.getStats(this.login, part)
    .subscribe(apiResult => {
      if (apiResult.success) {
        this.stats = apiResult.data;
      }
      else {
        this.message = apiResult.status;
      }
    })
  }

}
