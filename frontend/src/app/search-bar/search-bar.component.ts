import { Component, OnInit } from '@angular/core';
import { faSearch, faCaretRight } from '@fortawesome/free-solid-svg-icons';
import { FormBuilder, FormGroup } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-search-bar',
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.css']
})
export class SearchBarComponent implements OnInit {
  
  backendUrl: string = 'http://34.198.77.180:5000/';
  fireballURL: string = 'https://www.dnd5eapi.co/api/spells/fireball'

  faSearch = faSearch;
  faCaretRight = faCaretRight;
  
  beerForm!: FormGroup;
  formValues;
  brewMethods;
  autoCompleteSugg = [];

  searchResults;
  extraOptionsToggle = false;
  


  constructor(private fb: FormBuilder, 
              private http: HttpClient) { }

  ngOnInit(): void {
    this.initForm();
    this.lookUpBrewMethods();
    document.getElementById('searchInput').addEventListener('input', this.updateValue)
  }

  updateValue = (event) => {
    this.getAutoCompleteSuggestions(event.target.value);
  }

  initForm() {
    this.beerForm = this.fb.group({
      query: '',
      extraOptions: this.fb.group({
        minABV: '',
        maxABV: '',
        brewMethod: ''
      }),
    })
  }

  onSubmit() {
    this.formValues = this.beerForm.value;
    console.log(this.formValues);
    this.sendToBackend();
  }

  sendToBackend() {
    return new Promise(resolve => {
      this.http.post(this.backendUrl + 'search', this.formValues).toPromise().then((res) => {
        console.log(res);
        this.searchResults = res;
      });
    });
  }

  lookUpBrewMethods() {
    return new Promise(resolve => {
      this.http.get(this.backendUrl + 'brew').toPromise().then((res) => {
        this.brewMethods = res;
      });
    });
  } 

  openExtraOptions() {
    this.extraOptionsToggle = !this.extraOptionsToggle;
  }

  getAutoCompleteSuggestions(value) {
    return new Promise(resolve => {
      this.http.get(this.backendUrl + 'autocomplete?query=' + value).subscribe((res: any) => {
        this.autoCompleteSugg = res.results;
        console.log(res.results);
      });
    });
  } 
}
