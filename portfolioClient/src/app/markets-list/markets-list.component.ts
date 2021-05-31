import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-markets-list',
  templateUrl: './markets-list.component.html',
  styleUrls: ['./markets-list.component.css']
})
export class MarketsListComponent implements OnInit {
  markets: any[] = [];
  apiName: string = '';

  constructor(@Inject(MAT_DIALOG_DATA) public data: any) { 
    console.log(data);
    this.markets = data['markets'];
    this.apiName = data['apiName']
  }

  ngOnInit(): void {
  }

}
