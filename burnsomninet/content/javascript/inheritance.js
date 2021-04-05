/**
* @author Quintin Smith <smith.quintin@protonmail.com>
* @class
* @classdesc
* This is the object factory, so to speak. Instead of using functions as Classes we can use
* define_class, and specify the prototype and parent class all together.
* The difference is now grand parents of two different abstracted classes aren't a shared object when instantiated.
* @example
* define_class('SomeClass', {
*     init: function(somearg) {
*         var that = this;
*         that.value = somearg;
*     }
* });
* var somevar = new SomeClass(2);
*
* @example
* define_class('SomeSubClass', {
*     init: function(some_other_arg) {
*         var that = this;
*         that.super('init', some_other_arg);
*     }
* }, 'SomeClass');
*/
var ClassHandler = function() { };

ClassHandler.prototype = {
    defined: {},
    idgen: 0,
    classes: { },
    /**
        This is a wrapper that is called in attempt to call a super class's function
    */
    supermiddlefunc: function() {
        var that = this;
        var function_name = arguments[0];
        var args = [];
        for (var i = 1; i < arguments.length; i++) {
            args.push(arguments[i]);
        }

        if (! that.__super_levels[that.__uuid]) {
            that.__super_levels[that.__uuid] = {};
        }
        if (! that.__super_levels[that.__uuid][function_name]) {
            that.__super_levels[that.__uuid][function_name] = 0;
        }

        var level = that.__super_levels[that.__uuid][function_name];

        that.__super_levels[that.__uuid][function_name] += 1;

        var super_func = that.__super_funcs[function_name][level];
        if (! super_func) {
            throw 'Trying to run non-existent super function "' + function_name + '" from class "' + that.__name__ + '"';
        }
        var output = super_func.apply(that, args);

        that.__super_levels[that.__uuid][function_name] -= 1;


        return output;
    },

    /**
    * Referred to by isa. Checks if the defined Object is either the same class or a subclass of a given Type.
    * @param {Object} constructor The constructor of the type to be compared.
    * @example
    *    somecompound.isa(Compound);
    */
    _is_checker: function(constructor) {
        var that = this;
        var c = that.constructor;
        var output = false;

        while (c) {
            if (c == constructor) {
                output = true;
                break;
            } else {
                c = c.__super_constructor;
            }
        }

        return output;
    },

    /**
    * @param{String} class_name Name of the new class
    * @param{Object} template Effectively the 'prototype' if you were to define the class using function
    * @param{String} parent_class Name of the parent class
    */
    define_class: function(class_name, template, parent_class) {
        var that = this;

        template.__name__ = class_name;

        if (parent_class) {
            if (! that.classes[parent_class]) {
                throw ('"' + class_name + '" Attempting to subclass undefined: "' + parent_class + '"');
             } else {
                template.__super_constructor = that.classes[parent_class].constructor;
            }
        }

        var new_obj_constructor = function() {
            this.__uuid =  __CLASSHANDLER.idgen;
            __CLASSHANDLER.idgen += 1;
            if (this.init) {
                this.init.apply(this, arguments);
            }
        };

        new_obj_constructor.prototype.super = ClassHandler.prototype.supermiddlefunc;
        new_obj_constructor.prototype.isa = ClassHandler.prototype._is_checker;
        new_obj_constructor.isa = ClassHandler.prototype._is_checker;

        new_obj_constructor.prototype.__super_funcs = {};
        new_obj_constructor.prototype.__super_levels = {};

        var static_key, key;
        for (key in template) {
            // Give the constructor the ability to reproduce key values,
            new_obj_constructor.prototype[key] = template[key];
            // Give the constructor the ability to access key values,
            new_obj_constructor[key] = template[key];
        }

        if (parent_class && that.classes[parent_class]) {
            var par = that.classes[parent_class];
            new_obj_constructor.__super_constructor = par.constructor;
            while (par) {
                for (key in par.constructor) {
                    if (typeof new_obj_constructor.prototype[key] == 'undefined') {
                        new_obj_constructor.prototype[key] = par.constructor[key];
                    } else {
                        if (! new_obj_constructor.prototype.__super_funcs[key]) {
                            new_obj_constructor.prototype.__super_funcs[key] = [];
                        }
                        new_obj_constructor.prototype.__super_funcs[key].push(par.constructor[key]);
                    }
                }
                par = that.classes[par.parent_class];
            }
        }

        that.classes[class_name] = {
            constructor: new_obj_constructor,
            parent_class: parent_class
        };

        // Consider the environment being used...
        if (typeof global != "undefined") {
            global[class_name] = this.classes[class_name].constructor;
        } else {
            window[class_name] = this.classes[class_name].constructor;
        }
    }
};

// Wrappers for ClassHandler so No one has to type in '__CLASSHANDLER.define_class...'
var __CLASSHANDLER = new ClassHandler();
function define_class(class_name, template, parent_class) {
    __CLASSHANDLER.define_class(class_name, template, parent_class);
}



///////////////////////////////////////////////////////////////////
define_class('Compound', {
    /** @member {HTMLElement} */
    element: null,
    /** @member {Object} */
    default_options: {
        id: null,
        class: null,
        on: {}
    },

    /**
    * @abstract
    * @classdesc
    * Given a DOM object and some objects, used to create special widgits.
    * This is to replace jQuery's Widgit Factory objects.
    *
    * @constructs
    * @param {HTMLElement} element The DOM element around which the Compound is constructed
    * @param {Object} options Hashmap of optional properties.
    * @tutorial compound
    * @tutorial compound-static
    */
    init: function(element, options) {
        var that = this;
        that.element = element;

        if (! that.element.data) {
            that.element.data = {};
        }

        that.element.data.COMPOUND = that;
        that.element.data[that.__name__] = that;

        //////////////////////////////////////////////////////////////

        ///    TODO: This needs proper unit testing
        // We want to consolidate all options to allow for default values (3 Steps)
        var consolidated_options = options;
        var constructor = that.__proto__;


        while (constructor.__super_constructor) {
            for (var key in constructor.options) {
                if (typeof consolidated_options[key] == 'undefined') {
                    consolidated_options[key] = constructor.default_options[key];
                }
            }
            constructor = constructor.__super_constructor;
        }


        that.options = consolidated_options;

        ///////////////////////////////////////////////////////////////

        for (var k in options) {
            that.options[k] = options[k];
        }

        if (that.options.id) {
            that.element.id = that.options.id;
        }

        if (that.options.class) {
            that.element.addClass(that.options.class);
        }

        for (var eventname in that.options.on) {
            event_listen.call(that.element, eventname, function(event) {
                var spec_elm = this.data.COMPOUND;
                spec_elm.options.on[event.type].call(spec_elm, event);
            });
        }
    },

    /**
        Removes all of the HTMLElements within the element property
    */
    empty: function() {
        var that = this;
        while (that.element.firstChild) {
            that.element.removeChild(that.element.firstChild);
        }
    },
    /**
        Removes the Compound from the DOM
    */
    destroy: function() {
        var that = this;
        that.element.detach();
    },

    /**
        Detaches the Compound's Element from the DOM
    */
    detach: function() {
        var that = this;
        that.element.detach();
        that._rendered = false;
    }
});

var EVENTMAP = {}

function event_listen(eventname, function_hook) {
    var eventpath = eventname.split(".");
    var current_branch = EVENTMAP;
    for (var i in eventpath) {
        if (i == eventpath.length - 1) {
            break;
        } else if (!current_branch[eventpath[i]]) {
            current_branch[eventpath[i]] = {};
        }

        current_branch = current_branch[eventpath[i]];
    }

    var eventtype = eventpath[eventpath.length - 1];
    current_branch[eventtype] = function_hook;

    this.addEventListener(eventtype, function_hook);
}

function event_ignore(eventname, function_hook) {
    var eventpath = eventname.split(".");
    var current_branch = EVENTMAP;
    for (var i in eventpath) {
        if (i == eventpath.length - 1) {
            break;
        } else if (!current_branch[eventpath[i]]) {
            current_branch[eventpath[i]] = {};
        }

        current_branch = current_branch[eventpath[i]];
    }

    var eventtype = eventpath[eventpath.length - 1];
    this.removeEventListener(eventtype, current_branch[eventtype]);

    delete current_branch[eventtype];
}

