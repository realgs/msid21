import { Component, OnInit } from '@angular/core';
import { PortfolioService } from '../portfolio.service';
import { Api } from '../models/api';
import { CookieService } from 'ngx-cookie';
import { MatDialog } from '@angular/material/dialog';
import { MarketsListComponent } from '../markets-list/markets-list.component';

@Component({
  selector: 'app-available-apis',
  templateUrl: './available-apis.component.html',
  styleUrls: ['./available-apis.component.css']
})
export class AvailableApisComponent implements OnInit {
  apis: Api[] = [];

  constructor(private service: PortfolioService, private cookie: CookieService, public dialog: MatDialog) { }

  ngOnInit(): void {
    const login = this.cookie.get('portfolioLogin');
    if (login){
      this.service.availableApi(login)
      .subscribe(apiResult => {
        if (apiResult.success) {
        this.apis = apiResult.data;
      }});
    }
  }

  openDialog(api: Api){
    this.dialog.open(MarketsListComponent, {
      data: {
        apiName: api.name,
        markets: api.markets
      }
    });
  }
}
