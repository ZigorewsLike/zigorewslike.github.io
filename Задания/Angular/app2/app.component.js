"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var core_1 = require('@angular/core');
var Todo = (function () {
    function Todo(title, completed) {
        if (completed === void 0) { completed = false; }
        this.title = title;
        this.completed = completed;
    }
    return Todo;
}());
var todos = [
    { title: 'Изучить JavaScript',
        completed: true
    },
    { title: 'Изучить Angular 2',
        completed: false
    },
    { title: 'Написать приложение',
        completed: false
    }
];
var AppComponent = (function () {
    function AppComponent() {
        this.title = 'Angular 2';
        this.todos = todos;
        this.newTodoTitle = '';
        this.newTodoTitle2 = '';
    }
    AppComponent.prototype.create = function () {
        var onetext = (this.newTodoTitle);
        var twotext = (this.newTodoTitle2);
        var sumcredit = (onetext/twotext);
        sumcredit=sumcredit+((sumcredit/100)*12.9)
        document.getElementById('EnterNember').textContent="Сумма кредита " + onetext + " руб.";
        document.getElementById('EnterNember2').textContent="Срок кредита " + twotext + " мес.";
        document.getElementById('EnterNember3').textContent="Ежемесячный платеж " + sumcredit + " руб.";
    };
    AppComponent.prototype.toggle = function (todo) {
        todo.completed = !todo.completed;
    };
    AppComponent.prototype.delete = function (todo) {
        var index = this.todos.indexOf(todo);
        if (index > -1) {
            this.todos.splice(index, 1);
        }
    };
    AppComponent = __decorate([
        core_1.Component({
            moduleId: module.id,
            selector: 'app',
            templateUrl: 'app.component.html',
            styleUrls: ['app.component.css']
        }), 
        __metadata('design:paramtypes', [])
    ], AppComponent);
    return AppComponent;
}());
exports.AppComponent = AppComponent;
//# sourceMappingURL=app.component.js.map