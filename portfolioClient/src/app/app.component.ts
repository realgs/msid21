import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CookieService } from 'ngx-cookie';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  logged: boolean = false;
  login: string = '';

  constructor(private cookie: CookieService, private router: Router){  }

  ngOnInit(): void {
    this.onLogged();
  }

  onLogged(): void{
    this.login = this.cookie.get('portfolioLogin');
    if (this.login){
      this.logged = true;
      this.router.navigate(['portfolio']);
    }
  }

  logout(): void{
    this.cookie.remove('portfolioLogin');
    this.logged = false;
    this.router.navigate(['/']);
  }
}
