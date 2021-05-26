import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ArbitrationComponent } from './arbitration/arbitration.component';
import { AvailableApisComponent } from './available-apis/available-apis.component';
import { ConfigurationComponent } from './configuration/configuration.component';
import { LoginComponent } from './login/login.component';
import { PortfolioComponent } from './portfolio/portfolio.component';
import { ProfitComponent } from './profit/profit.component';
import { ResourcesComponent } from './resources/resources.component';

const routes: Routes = [
  {path: '', component: LoginComponent},
  {path: 'login', component: LoginComponent},
  {path: 'availableApi', component: AvailableApisComponent},
  {path: 'portfolio', component: PortfolioComponent},
  {path: 'configuration', component: ConfigurationComponent},
  {path: 'arbitrations', component: ArbitrationComponent},
  {path: 'profit', component: ProfitComponent},
  {path: 'resources', component: ResourcesComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
