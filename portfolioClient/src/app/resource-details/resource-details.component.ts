import { Component, Inject } from '@angular/core';
import {MatDialog, MAT_DIALOG_DATA} from '@angular/material/dialog';
import { ResourceStats } from '../models/resourceStats';

@Component({
  selector: 'app-resource-details',
  templateUrl: './resource-details.component.html',
  styleUrls: ['./resource-details.component.css']
})
export class ResourceDetailsComponent {

  constructor(@Inject(MAT_DIALOG_DATA) public data: ResourceStats) {
    console.log(data);
   }

  ngOnInit(): void {
  }

}
