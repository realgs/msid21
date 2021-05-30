import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './login/login.component';
import { MatInputModule } from '@angular/material/input';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatButtonModule} from '@angular/material/button';
import { HttpClientModule } from '@angular/common/http';
import { ResourceDetailsComponent } from './resource-details/resource-details.component';
import { AvailableApisComponent } from './available-apis/available-apis.component';
import { ConfigurationComponent } from './configuration/configuration.component';
import { CookieModule } from 'ngx-cookie';
import {MatSelectModule} from '@angular/material/select';
import { ArbitrationComponent } from './arbitration/arbitration.component';
import { ValueAndProfitComponent } from './valueAndProfit/valueAndProfit.component';
import { ResourcesComponent } from './resources/resources.component';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    ResourceDetailsComponent,
    AvailableApisComponent,
    ConfigurationComponent,
    ArbitrationComponent,
    ValueAndProfitComponent,
    ResourcesComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    FormsModule,
    MatInputModule,
    MatButtonModule,
    HttpClientModule,
    MatSelectModule,
    ReactiveFormsModule,
    CookieModule.forRoot()
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
