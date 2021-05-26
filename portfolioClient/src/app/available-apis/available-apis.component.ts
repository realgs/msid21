import { Component, OnInit } from '@angular/core';
import { PortfolioService } from '../portfolio.service';
import { Api } from '../models/api';
import { ApiResult } from '../models/apiResult';

@Component({
  selector: 'app-available-apis',
  templateUrl: './available-apis.component.html',
  styleUrls: ['./available-apis.component.css']
})
export class AvailableApisComponent implements OnInit {
  apis: Api[] = [];

  constructor(private service: PortfolioService) { }

  ngOnInit(): void {
    this.service.availableApi()
    .subscribe(apiResult => {
      if (apiResult.success) {
      this.apis = apiResult.data;
    }});
  }
}
