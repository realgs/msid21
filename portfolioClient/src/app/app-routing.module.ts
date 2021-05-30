import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ArbitrationComponent } from './arbitration/arbitration.component';
import { AvailableApisComponent } from './available-apis/available-apis.component';
import { ConfigurationComponent } from './configuration/configuration.component';
import { LoginComponent } from './login/login.component';
import { ValueAndProfitComponent } from './valueAndProfit/valueAndProfit.component';
import { ResourcesComponent } from './resources/resources.component';

const routes: Routes = [
  {path: '', component: LoginComponent},
  {path: 'login', component: LoginComponent},
  {path: 'availableApi', component: AvailableApisComponent},
  {path: 'configuration', component: ConfigurationComponent},
  {path: 'arbitrations', component: ArbitrationComponent},
  {path: 'stats', component: ValueAndProfitComponent},
  {path: 'resources', component: ResourcesComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
