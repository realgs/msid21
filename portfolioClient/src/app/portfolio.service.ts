import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Api } from './models/api';
import { ApiResult } from './models/apiResult';

@Injectable({
  providedIn: 'root'
})
export class PortfolioService {
  private baseUrl: string = 'http://127.0.0.1:5000/api/';

  constructor(private http: HttpClient) { }

  load(login: string): Observable<ApiResult> {
    const url = this.baseUrl + 'load?login=' + login;
    return this.http.post<ApiResult>(url, ''); 
  }

  getStats(login: string, part?: number): Observable<ApiResult> {
    let url = this.baseUrl + 'stats?login=' + login;
    if (part){
      url = url + '&part=' + part;
    }
    return this.http.get<ApiResult>(url); 
  }

  addResource(login: string, name: string, amount: number, price: number): Observable<ApiResult> {
    let url = this.baseUrl + 'addResource?login=' + login + '&name=' + name + '&amount=' + amount + '&price=' + price;
    return this.http.post<ApiResult>(url, '');
  }

  removeResource(login: string, name: string, amount: number): Observable<ApiResult> {
    let url = this.baseUrl + 'removeResource?login=' + login + '&name=' + name + '&amount=' + amount;
    return this.http.post<ApiResult>(url, '');
  }

  getResources(login: string): Observable<ApiResult> {
    let url = this.baseUrl + 'getResources?login=' + login;
    return this.http.get<ApiResult>(url); 
  }

  getValue(login: string, part: number): Observable<ApiResult> {
    let url = this.baseUrl + 'portfolioValue?login=' + login + "&part=" + part;
    return this.http.get<ApiResult>(url); 
  }

  getProfits(login: string, part: number): Observable<ApiResult> {
    let url = this.baseUrl + 'profit?login=' + login + "&part=" + part;
    return this.http.get<ApiResult>(url); 
  }

  getArbitrations(login: string, resource?: string): Observable<ApiResult> {
    let url = this.baseUrl + 'arbitration?login=' + login;
    if (resource){
      url = url + '&resource=' + resource;
    }
    return this.http.get<ApiResult>(url); 
  }

  getConfiguration(login: string): Observable<ApiResult> {
    let url = this.baseUrl + 'getConfiguration?login=' + login;
    return this.http.get<ApiResult>(url);
  }

  setConfiguration(login: string, currency: number, fee: number): Observable<ApiResult> {
    let url = this.baseUrl + 'setConfiguration?login=' + login + '&currency=' + currency + '&fee=' + fee;
    return this.http.post<ApiResult>(url, '');
  }

  availableApi(login: string): Observable<ApiResult> {
    const url = this.baseUrl + 'available?login=' + login;
    return this.http.get<ApiResult>(url);
  }
}
