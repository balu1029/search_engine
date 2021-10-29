import { Component, OnInit } from '@angular/core';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import { FormBuilder, FormGroup } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-search-bar',
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.css']
})
export class SearchBarComponent implements OnInit {
  
  backendUrl: string = 'http://34.198.77.180:5000/search';
  fireballURL: string = 'https://www.dnd5eapi.co/api/spells/fireball'

  faSearch = faSearch;
  
  beerForm!: FormGroup;
  formForBackend: any;

  searchResults;

  constructor(private fb: FormBuilder, 
              private http: HttpClient) { }

  ngOnInit(): void {
    this.initForm();

    this.beerForm.valueChanges.subscribe(console.log)
  }

  initForm() {
    this.beerForm = this.fb.group({
      query: '',
      minABV: '',
      maxABV: '',
      brewMethod: ''
    })
  }

  onSubmit() {
    this.formForBackend = this.beerForm;
    console.log(this.formForBackend);
    //this.sendToBackend();
  }

  sendToBackend() {
    return new Promise(resolve => {
      this.http.post(this.backendUrl, this.formForBackend).toPromise().then((res) => {
        this.searchResults = res;
      });
    });
  }
}
