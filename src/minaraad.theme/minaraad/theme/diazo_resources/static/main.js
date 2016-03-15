/*!
 * Masonry PACKAGED v3.3.2
 * Cascading grid layout library
 * http://masonry.desandro.com
 * MIT License
 * by David DeSandro
 */
!function(window) {
    function noop() {}
    function defineBridget($) {
        function addOptionMethod(PluginClass) {
            PluginClass.prototype.option || (PluginClass.prototype.option = function(opts) {
                $.isPlainObject(opts) && (this.options = $.extend(!0, this.options, opts));
            });
        }
        function bridge(namespace, PluginClass) {
            $.fn[namespace] = function(options) {
                if ("string" == typeof options) {
                    for (var args = slice.call(arguments, 1), i = 0, len = this.length; len > i; i++) {
                        var elem = this[i], instance = $.data(elem, namespace);
                        if (instance) if ($.isFunction(instance[options]) && "_" !== options.charAt(0)) {
                            var returnValue = instance[options].apply(instance, args);
                            if (void 0 !== returnValue) return returnValue;
                        } else logError("no such method '" + options + "' for " + namespace + " instance"); else logError("cannot call methods on " + namespace + " prior to initialization; attempted to call '" + options + "'");
                    }
                    return this;
                }
                return this.each(function() {
                    var instance = $.data(this, namespace);
                    instance ? (instance.option(options), instance._init()) : (instance = new PluginClass(this, options), 
                    $.data(this, namespace, instance));
                });
            };
        }
        if ($) {
            var logError = "undefined" == typeof console ? noop : function(message) {
                console.error(message);
            };
            return $.bridget = function(namespace, PluginClass) {
                addOptionMethod(PluginClass), bridge(namespace, PluginClass);
            }, $.bridget;
        }
    }
    var slice = Array.prototype.slice;
    "function" == typeof define && define.amd ? define("jquery-bridget/jquery.bridget", [ "jquery" ], defineBridget) : defineBridget("object" == typeof exports ? require("jquery") : window.jQuery);
}(window), /*!
 * eventie v1.0.6
 * event binding helper
 *   eventie.bind( elem, 'click', myFn )
 *   eventie.unbind( elem, 'click', myFn )
 * MIT license
 */
function(window) {
    function getIEEvent(obj) {
        var event = window.event;
        return event.target = event.target || event.srcElement || obj, event;
    }
    var docElem = document.documentElement, bind = function() {};
    docElem.addEventListener ? bind = function(obj, type, fn) {
        obj.addEventListener(type, fn, !1);
    } : docElem.attachEvent && (bind = function(obj, type, fn) {
        obj[type + fn] = fn.handleEvent ? function() {
            var event = getIEEvent(obj);
            fn.handleEvent.call(fn, event);
        } : function() {
            var event = getIEEvent(obj);
            fn.call(obj, event);
        }, obj.attachEvent("on" + type, obj[type + fn]);
    });
    var unbind = function() {};
    docElem.removeEventListener ? unbind = function(obj, type, fn) {
        obj.removeEventListener(type, fn, !1);
    } : docElem.detachEvent && (unbind = function(obj, type, fn) {
        obj.detachEvent("on" + type, obj[type + fn]);
        try {
            delete obj[type + fn];
        } catch (err) {
            obj[type + fn] = void 0;
        }
    });
    var eventie = {
        bind: bind,
        unbind: unbind
    };
    "function" == typeof define && define.amd ? define("eventie/eventie", eventie) : "object" == typeof exports ? module.exports = eventie : window.eventie = eventie;
}(window), function() {
    function EventEmitter() {}
    function indexOfListener(listeners, listener) {
        for (var i = listeners.length; i--; ) if (listeners[i].listener === listener) return i;
        return -1;
    }
    function alias(name) {
        return function() {
            return this[name].apply(this, arguments);
        };
    }
    var proto = EventEmitter.prototype, exports = this, originalGlobalValue = exports.EventEmitter;
    proto.getListeners = function(evt) {
        var response, key, events = this._getEvents();
        if (evt instanceof RegExp) {
            response = {};
            for (key in events) events.hasOwnProperty(key) && evt.test(key) && (response[key] = events[key]);
        } else response = events[evt] || (events[evt] = []);
        return response;
    }, proto.flattenListeners = function(listeners) {
        var i, flatListeners = [];
        for (i = 0; i < listeners.length; i += 1) flatListeners.push(listeners[i].listener);
        return flatListeners;
    }, proto.getListenersAsObject = function(evt) {
        var response, listeners = this.getListeners(evt);
        return listeners instanceof Array && (response = {}, response[evt] = listeners), 
        response || listeners;
    }, proto.addListener = function(evt, listener) {
        var key, listeners = this.getListenersAsObject(evt), listenerIsWrapped = "object" == typeof listener;
        for (key in listeners) listeners.hasOwnProperty(key) && -1 === indexOfListener(listeners[key], listener) && listeners[key].push(listenerIsWrapped ? listener : {
            listener: listener,
            once: !1
        });
        return this;
    }, proto.on = alias("addListener"), proto.addOnceListener = function(evt, listener) {
        return this.addListener(evt, {
            listener: listener,
            once: !0
        });
    }, proto.once = alias("addOnceListener"), proto.defineEvent = function(evt) {
        return this.getListeners(evt), this;
    }, proto.defineEvents = function(evts) {
        for (var i = 0; i < evts.length; i += 1) this.defineEvent(evts[i]);
        return this;
    }, proto.removeListener = function(evt, listener) {
        var index, key, listeners = this.getListenersAsObject(evt);
        for (key in listeners) listeners.hasOwnProperty(key) && (index = indexOfListener(listeners[key], listener), 
        -1 !== index && listeners[key].splice(index, 1));
        return this;
    }, proto.off = alias("removeListener"), proto.addListeners = function(evt, listeners) {
        return this.manipulateListeners(!1, evt, listeners);
    }, proto.removeListeners = function(evt, listeners) {
        return this.manipulateListeners(!0, evt, listeners);
    }, proto.manipulateListeners = function(remove, evt, listeners) {
        var i, value, single = remove ? this.removeListener : this.addListener, multiple = remove ? this.removeListeners : this.addListeners;
        if ("object" != typeof evt || evt instanceof RegExp) for (i = listeners.length; i--; ) single.call(this, evt, listeners[i]); else for (i in evt) evt.hasOwnProperty(i) && (value = evt[i]) && ("function" == typeof value ? single.call(this, i, value) : multiple.call(this, i, value));
        return this;
    }, proto.removeEvent = function(evt) {
        var key, type = typeof evt, events = this._getEvents();
        if ("string" === type) delete events[evt]; else if (evt instanceof RegExp) for (key in events) events.hasOwnProperty(key) && evt.test(key) && delete events[key]; else delete this._events;
        return this;
    }, proto.removeAllListeners = alias("removeEvent"), proto.emitEvent = function(evt, args) {
        var listener, i, key, response, listeners = this.getListenersAsObject(evt);
        for (key in listeners) if (listeners.hasOwnProperty(key)) for (i = listeners[key].length; i--; ) listener = listeners[key][i], 
        listener.once === !0 && this.removeListener(evt, listener.listener), response = listener.listener.apply(this, args || []), 
        response === this._getOnceReturnValue() && this.removeListener(evt, listener.listener);
        return this;
    }, proto.trigger = alias("emitEvent"), proto.emit = function(evt) {
        var args = Array.prototype.slice.call(arguments, 1);
        return this.emitEvent(evt, args);
    }, proto.setOnceReturnValue = function(value) {
        return this._onceReturnValue = value, this;
    }, proto._getOnceReturnValue = function() {
        return this.hasOwnProperty("_onceReturnValue") ? this._onceReturnValue : !0;
    }, proto._getEvents = function() {
        return this._events || (this._events = {});
    }, EventEmitter.noConflict = function() {
        return exports.EventEmitter = originalGlobalValue, EventEmitter;
    }, "function" == typeof define && define.amd ? define("eventEmitter/EventEmitter", [], function() {
        return EventEmitter;
    }) : "object" == typeof module && module.exports ? module.exports = EventEmitter : exports.EventEmitter = EventEmitter;
}.call(this), /*!
 * getStyleProperty v1.0.4
 * original by kangax
 * http://perfectionkills.com/feature-testing-css-properties/
 * MIT license
 */
function(window) {
    function getStyleProperty(propName) {
        if (propName) {
            if ("string" == typeof docElemStyle[propName]) return propName;
            propName = propName.charAt(0).toUpperCase() + propName.slice(1);
            for (var prefixed, i = 0, len = prefixes.length; len > i; i++) if (prefixed = prefixes[i] + propName, 
            "string" == typeof docElemStyle[prefixed]) return prefixed;
        }
    }
    var prefixes = "Webkit Moz ms Ms O".split(" "), docElemStyle = document.documentElement.style;
    "function" == typeof define && define.amd ? define("get-style-property/get-style-property", [], function() {
        return getStyleProperty;
    }) : "object" == typeof exports ? module.exports = getStyleProperty : window.getStyleProperty = getStyleProperty;
}(window), /*!
 * getSize v1.2.2
 * measure size of elements
 * MIT license
 */
function(window, undefined) {
    function getStyleSize(value) {
        var num = parseFloat(value), isValid = -1 === value.indexOf("%") && !isNaN(num);
        return isValid && num;
    }
    function noop() {}
    function getZeroSize() {
        for (var size = {
            width: 0,
            height: 0,
            innerWidth: 0,
            innerHeight: 0,
            outerWidth: 0,
            outerHeight: 0
        }, i = 0, len = measurements.length; len > i; i++) {
            var measurement = measurements[i];
            size[measurement] = 0;
        }
        return size;
    }
    function defineGetSize(getStyleProperty) {
        function setup() {
            if (!isSetup) {
                isSetup = !0;
                var getComputedStyle = window.getComputedStyle;
                if (getStyle = function() {
                    var getStyleFn = getComputedStyle ? function(elem) {
                        return getComputedStyle(elem, null);
                    } : function(elem) {
                        return elem.currentStyle;
                    };
                    return function(elem) {
                        var style = getStyleFn(elem);
                        return style || logError("Style returned " + style + ". Are you running this code in a hidden iframe on Firefox? See http://bit.ly/getsizebug1"), 
                        style;
                    };
                }(), boxSizingProp = getStyleProperty("boxSizing")) {
                    var div = document.createElement("div");
                    div.style.width = "200px", div.style.padding = "1px 2px 3px 4px", div.style.borderStyle = "solid", 
                    div.style.borderWidth = "1px 2px 3px 4px", div.style[boxSizingProp] = "border-box";
                    var body = document.body || document.documentElement;
                    body.appendChild(div);
                    var style = getStyle(div);
                    isBoxSizeOuter = 200 === getStyleSize(style.width), body.removeChild(div);
                }
            }
        }
        function getSize(elem) {
            if (setup(), "string" == typeof elem && (elem = document.querySelector(elem)), elem && "object" == typeof elem && elem.nodeType) {
                var style = getStyle(elem);
                if ("none" === style.display) return getZeroSize();
                var size = {};
                size.width = elem.offsetWidth, size.height = elem.offsetHeight;
                for (var isBorderBox = size.isBorderBox = !(!boxSizingProp || !style[boxSizingProp] || "border-box" !== style[boxSizingProp]), i = 0, len = measurements.length; len > i; i++) {
                    var measurement = measurements[i], value = style[measurement];
                    value = mungeNonPixel(elem, value);
                    var num = parseFloat(value);
                    size[measurement] = isNaN(num) ? 0 : num;
                }
                var paddingWidth = size.paddingLeft + size.paddingRight, paddingHeight = size.paddingTop + size.paddingBottom, marginWidth = size.marginLeft + size.marginRight, marginHeight = size.marginTop + size.marginBottom, borderWidth = size.borderLeftWidth + size.borderRightWidth, borderHeight = size.borderTopWidth + size.borderBottomWidth, isBorderBoxSizeOuter = isBorderBox && isBoxSizeOuter, styleWidth = getStyleSize(style.width);
                styleWidth !== !1 && (size.width = styleWidth + (isBorderBoxSizeOuter ? 0 : paddingWidth + borderWidth));
                var styleHeight = getStyleSize(style.height);
                return styleHeight !== !1 && (size.height = styleHeight + (isBorderBoxSizeOuter ? 0 : paddingHeight + borderHeight)), 
                size.innerWidth = size.width - (paddingWidth + borderWidth), size.innerHeight = size.height - (paddingHeight + borderHeight), 
                size.outerWidth = size.width + marginWidth, size.outerHeight = size.height + marginHeight, 
                size;
            }
        }
        function mungeNonPixel(elem, value) {
            if (window.getComputedStyle || -1 === value.indexOf("%")) return value;
            var style = elem.style, left = style.left, rs = elem.runtimeStyle, rsLeft = rs && rs.left;
            return rsLeft && (rs.left = elem.currentStyle.left), style.left = value, value = style.pixelLeft, 
            style.left = left, rsLeft && (rs.left = rsLeft), value;
        }
        var getStyle, boxSizingProp, isBoxSizeOuter, isSetup = !1;
        return getSize;
    }
    var logError = "undefined" == typeof console ? noop : function(message) {
        console.error(message);
    }, measurements = [ "paddingLeft", "paddingRight", "paddingTop", "paddingBottom", "marginLeft", "marginRight", "marginTop", "marginBottom", "borderLeftWidth", "borderRightWidth", "borderTopWidth", "borderBottomWidth" ];
    "function" == typeof define && define.amd ? define("get-size/get-size", [ "get-style-property/get-style-property" ], defineGetSize) : "object" == typeof exports ? module.exports = defineGetSize(require("desandro-get-style-property")) : window.getSize = defineGetSize(window.getStyleProperty);
}(window), /*!
 * docReady v1.0.4
 * Cross browser DOMContentLoaded event emitter
 * MIT license
 */
function(window) {
    function docReady(fn) {
        "function" == typeof fn && (docReady.isReady ? fn() : queue.push(fn));
    }
    function onReady(event) {
        var isIE8NotReady = "readystatechange" === event.type && "complete" !== document.readyState;
        docReady.isReady || isIE8NotReady || trigger();
    }
    function trigger() {
        docReady.isReady = !0;
        for (var i = 0, len = queue.length; len > i; i++) {
            var fn = queue[i];
            fn();
        }
    }
    function defineDocReady(eventie) {
        return "complete" === document.readyState ? trigger() : (eventie.bind(document, "DOMContentLoaded", onReady), 
        eventie.bind(document, "readystatechange", onReady), eventie.bind(window, "load", onReady)), 
        docReady;
    }
    var document = window.document, queue = [];
    docReady.isReady = !1, "function" == typeof define && define.amd ? define("doc-ready/doc-ready", [ "eventie/eventie" ], defineDocReady) : "object" == typeof exports ? module.exports = defineDocReady(require("eventie")) : window.docReady = defineDocReady(window.eventie);
}(window), function(ElemProto) {
    function match(elem, selector) {
        return elem[matchesMethod](selector);
    }
    function checkParent(elem) {
        if (!elem.parentNode) {
            var fragment = document.createDocumentFragment();
            fragment.appendChild(elem);
        }
    }
    function query(elem, selector) {
        checkParent(elem);
        for (var elems = elem.parentNode.querySelectorAll(selector), i = 0, len = elems.length; len > i; i++) if (elems[i] === elem) return !0;
        return !1;
    }
    function matchChild(elem, selector) {
        return checkParent(elem), match(elem, selector);
    }
    var matchesSelector, matchesMethod = function() {
        if (ElemProto.matches) return "matches";
        if (ElemProto.matchesSelector) return "matchesSelector";
        for (var prefixes = [ "webkit", "moz", "ms", "o" ], i = 0, len = prefixes.length; len > i; i++) {
            var prefix = prefixes[i], method = prefix + "MatchesSelector";
            if (ElemProto[method]) return method;
        }
    }();
    if (matchesMethod) {
        var div = document.createElement("div"), supportsOrphans = match(div, "div");
        matchesSelector = supportsOrphans ? match : matchChild;
    } else matchesSelector = query;
    "function" == typeof define && define.amd ? define("matches-selector/matches-selector", [], function() {
        return matchesSelector;
    }) : "object" == typeof exports ? module.exports = matchesSelector : window.matchesSelector = matchesSelector;
}(Element.prototype), function(window, factory) {
    "function" == typeof define && define.amd ? define("fizzy-ui-utils/utils", [ "doc-ready/doc-ready", "matches-selector/matches-selector" ], function(docReady, matchesSelector) {
        return factory(window, docReady, matchesSelector);
    }) : "object" == typeof exports ? module.exports = factory(window, require("doc-ready"), require("desandro-matches-selector")) : window.fizzyUIUtils = factory(window, window.docReady, window.matchesSelector);
}(window, function(window, docReady, matchesSelector) {
    var utils = {};
    utils.extend = function(a, b) {
        for (var prop in b) a[prop] = b[prop];
        return a;
    }, utils.modulo = function(num, div) {
        return (num % div + div) % div;
    };
    var objToString = Object.prototype.toString;
    utils.isArray = function(obj) {
        return "[object Array]" == objToString.call(obj);
    }, utils.makeArray = function(obj) {
        var ary = [];
        if (utils.isArray(obj)) ary = obj; else if (obj && "number" == typeof obj.length) for (var i = 0, len = obj.length; len > i; i++) ary.push(obj[i]); else ary.push(obj);
        return ary;
    }, utils.indexOf = Array.prototype.indexOf ? function(ary, obj) {
        return ary.indexOf(obj);
    } : function(ary, obj) {
        for (var i = 0, len = ary.length; len > i; i++) if (ary[i] === obj) return i;
        return -1;
    }, utils.removeFrom = function(ary, obj) {
        var index = utils.indexOf(ary, obj);
        -1 != index && ary.splice(index, 1);
    }, utils.isElement = "function" == typeof HTMLElement || "object" == typeof HTMLElement ? function(obj) {
        return obj instanceof HTMLElement;
    } : function(obj) {
        return obj && "object" == typeof obj && 1 == obj.nodeType && "string" == typeof obj.nodeName;
    }, utils.setText = function() {
        function setText(elem, text) {
            setTextProperty = setTextProperty || (void 0 !== document.documentElement.textContent ? "textContent" : "innerText"), 
            elem[setTextProperty] = text;
        }
        var setTextProperty;
        return setText;
    }(), utils.getParent = function(elem, selector) {
        for (;elem != document.body; ) if (elem = elem.parentNode, matchesSelector(elem, selector)) return elem;
    }, utils.getQueryElement = function(elem) {
        return "string" == typeof elem ? document.querySelector(elem) : elem;
    }, utils.handleEvent = function(event) {
        var method = "on" + event.type;
        this[method] && this[method](event);
    }, utils.filterFindElements = function(elems, selector) {
        elems = utils.makeArray(elems);
        for (var ffElems = [], i = 0, len = elems.length; len > i; i++) {
            var elem = elems[i];
            if (utils.isElement(elem)) if (selector) {
                matchesSelector(elem, selector) && ffElems.push(elem);
                for (var childElems = elem.querySelectorAll(selector), j = 0, jLen = childElems.length; jLen > j; j++) ffElems.push(childElems[j]);
            } else ffElems.push(elem);
        }
        return ffElems;
    }, utils.debounceMethod = function(_class, methodName, threshold) {
        var method = _class.prototype[methodName], timeoutName = methodName + "Timeout";
        _class.prototype[methodName] = function() {
            var timeout = this[timeoutName];
            timeout && clearTimeout(timeout);
            var args = arguments, _this = this;
            this[timeoutName] = setTimeout(function() {
                method.apply(_this, args), delete _this[timeoutName];
            }, threshold || 100);
        };
    }, utils.toDashed = function(str) {
        return str.replace(/(.)([A-Z])/g, function(match, $1, $2) {
            return $1 + "-" + $2;
        }).toLowerCase();
    };
    var console = window.console;
    return utils.htmlInit = function(WidgetClass, namespace) {
        docReady(function() {
            for (var dashedNamespace = utils.toDashed(namespace), elems = document.querySelectorAll(".js-" + dashedNamespace), dataAttr = "data-" + dashedNamespace + "-options", i = 0, len = elems.length; len > i; i++) {
                var options, elem = elems[i], attr = elem.getAttribute(dataAttr);
                try {
                    options = attr && JSON.parse(attr);
                } catch (error) {
                    console && console.error("Error parsing " + dataAttr + " on " + elem.nodeName.toLowerCase() + (elem.id ? "#" + elem.id : "") + ": " + error);
                    continue;
                }
                var instance = new WidgetClass(elem, options), jQuery = window.jQuery;
                jQuery && jQuery.data(elem, namespace, instance);
            }
        });
    }, utils;
}), function(window, factory) {
    "function" == typeof define && define.amd ? define("outlayer/item", [ "eventEmitter/EventEmitter", "get-size/get-size", "get-style-property/get-style-property", "fizzy-ui-utils/utils" ], function(EventEmitter, getSize, getStyleProperty, utils) {
        return factory(window, EventEmitter, getSize, getStyleProperty, utils);
    }) : "object" == typeof exports ? module.exports = factory(window, require("wolfy87-eventemitter"), require("get-size"), require("desandro-get-style-property"), require("fizzy-ui-utils")) : (window.Outlayer = {}, 
    window.Outlayer.Item = factory(window, window.EventEmitter, window.getSize, window.getStyleProperty, window.fizzyUIUtils));
}(window, function(window, EventEmitter, getSize, getStyleProperty, utils) {
    function isEmptyObj(obj) {
        for (var prop in obj) return !1;
        return prop = null, !0;
    }
    function Item(element, layout) {
        element && (this.element = element, this.layout = layout, this.position = {
            x: 0,
            y: 0
        }, this._create());
    }
    function toDashedAll(str) {
        return str.replace(/([A-Z])/g, function($1) {
            return "-" + $1.toLowerCase();
        });
    }
    var getComputedStyle = window.getComputedStyle, getStyle = getComputedStyle ? function(elem) {
        return getComputedStyle(elem, null);
    } : function(elem) {
        return elem.currentStyle;
    }, transitionProperty = getStyleProperty("transition"), transformProperty = getStyleProperty("transform"), supportsCSS3 = transitionProperty && transformProperty, is3d = !!getStyleProperty("perspective"), transitionEndEvent = {
        WebkitTransition: "webkitTransitionEnd",
        MozTransition: "transitionend",
        OTransition: "otransitionend",
        transition: "transitionend"
    }[transitionProperty], prefixableProperties = [ "transform", "transition", "transitionDuration", "transitionProperty" ], vendorProperties = function() {
        for (var cache = {}, i = 0, len = prefixableProperties.length; len > i; i++) {
            var prop = prefixableProperties[i], supportedProp = getStyleProperty(prop);
            supportedProp && supportedProp !== prop && (cache[prop] = supportedProp);
        }
        return cache;
    }();
    utils.extend(Item.prototype, EventEmitter.prototype), Item.prototype._create = function() {
        this._transn = {
            ingProperties: {},
            clean: {},
            onEnd: {}
        }, this.css({
            position: "absolute"
        });
    }, Item.prototype.handleEvent = function(event) {
        var method = "on" + event.type;
        this[method] && this[method](event);
    }, Item.prototype.getSize = function() {
        this.size = getSize(this.element);
    }, Item.prototype.css = function(style) {
        var elemStyle = this.element.style;
        for (var prop in style) {
            var supportedProp = vendorProperties[prop] || prop;
            elemStyle[supportedProp] = style[prop];
        }
    }, Item.prototype.getPosition = function() {
        var style = getStyle(this.element), layoutOptions = this.layout.options, isOriginLeft = layoutOptions.isOriginLeft, isOriginTop = layoutOptions.isOriginTop, xValue = style[isOriginLeft ? "left" : "right"], yValue = style[isOriginTop ? "top" : "bottom"], layoutSize = this.layout.size, x = -1 != xValue.indexOf("%") ? parseFloat(xValue) / 100 * layoutSize.width : parseInt(xValue, 10), y = -1 != yValue.indexOf("%") ? parseFloat(yValue) / 100 * layoutSize.height : parseInt(yValue, 10);
        x = isNaN(x) ? 0 : x, y = isNaN(y) ? 0 : y, x -= isOriginLeft ? layoutSize.paddingLeft : layoutSize.paddingRight, 
        y -= isOriginTop ? layoutSize.paddingTop : layoutSize.paddingBottom, this.position.x = x, 
        this.position.y = y;
    }, Item.prototype.layoutPosition = function() {
        var layoutSize = this.layout.size, layoutOptions = this.layout.options, style = {}, xPadding = layoutOptions.isOriginLeft ? "paddingLeft" : "paddingRight", xProperty = layoutOptions.isOriginLeft ? "left" : "right", xResetProperty = layoutOptions.isOriginLeft ? "right" : "left", x = this.position.x + layoutSize[xPadding];
        style[xProperty] = this.getXValue(x), style[xResetProperty] = "";
        var yPadding = layoutOptions.isOriginTop ? "paddingTop" : "paddingBottom", yProperty = layoutOptions.isOriginTop ? "top" : "bottom", yResetProperty = layoutOptions.isOriginTop ? "bottom" : "top", y = this.position.y + layoutSize[yPadding];
        style[yProperty] = this.getYValue(y), style[yResetProperty] = "", this.css(style), 
        this.emitEvent("layout", [ this ]);
    }, Item.prototype.getXValue = function(x) {
        var layoutOptions = this.layout.options;
        return layoutOptions.percentPosition && !layoutOptions.isHorizontal ? x / this.layout.size.width * 100 + "%" : x + "px";
    }, Item.prototype.getYValue = function(y) {
        var layoutOptions = this.layout.options;
        return layoutOptions.percentPosition && layoutOptions.isHorizontal ? y / this.layout.size.height * 100 + "%" : y + "px";
    }, Item.prototype._transitionTo = function(x, y) {
        this.getPosition();
        var curX = this.position.x, curY = this.position.y, compareX = parseInt(x, 10), compareY = parseInt(y, 10), didNotMove = compareX === this.position.x && compareY === this.position.y;
        if (this.setPosition(x, y), didNotMove && !this.isTransitioning) return void this.layoutPosition();
        var transX = x - curX, transY = y - curY, transitionStyle = {};
        transitionStyle.transform = this.getTranslate(transX, transY), this.transition({
            to: transitionStyle,
            onTransitionEnd: {
                transform: this.layoutPosition
            },
            isCleaning: !0
        });
    }, Item.prototype.getTranslate = function(x, y) {
        var layoutOptions = this.layout.options;
        return x = layoutOptions.isOriginLeft ? x : -x, y = layoutOptions.isOriginTop ? y : -y, 
        is3d ? "translate3d(" + x + "px, " + y + "px, 0)" : "translate(" + x + "px, " + y + "px)";
    }, Item.prototype.goTo = function(x, y) {
        this.setPosition(x, y), this.layoutPosition();
    }, Item.prototype.moveTo = supportsCSS3 ? Item.prototype._transitionTo : Item.prototype.goTo, 
    Item.prototype.setPosition = function(x, y) {
        this.position.x = parseInt(x, 10), this.position.y = parseInt(y, 10);
    }, Item.prototype._nonTransition = function(args) {
        this.css(args.to), args.isCleaning && this._removeStyles(args.to);
        for (var prop in args.onTransitionEnd) args.onTransitionEnd[prop].call(this);
    }, Item.prototype._transition = function(args) {
        if (!parseFloat(this.layout.options.transitionDuration)) return void this._nonTransition(args);
        var _transition = this._transn;
        for (var prop in args.onTransitionEnd) _transition.onEnd[prop] = args.onTransitionEnd[prop];
        for (prop in args.to) _transition.ingProperties[prop] = !0, args.isCleaning && (_transition.clean[prop] = !0);
        if (args.from) {
            this.css(args.from);
            var h = this.element.offsetHeight;
            h = null;
        }
        this.enableTransition(args.to), this.css(args.to), this.isTransitioning = !0;
    };
    var transitionProps = "opacity," + toDashedAll(vendorProperties.transform || "transform");
    Item.prototype.enableTransition = function() {
        this.isTransitioning || (this.css({
            transitionProperty: transitionProps,
            transitionDuration: this.layout.options.transitionDuration
        }), this.element.addEventListener(transitionEndEvent, this, !1));
    }, Item.prototype.transition = Item.prototype[transitionProperty ? "_transition" : "_nonTransition"], 
    Item.prototype.onwebkitTransitionEnd = function(event) {
        this.ontransitionend(event);
    }, Item.prototype.onotransitionend = function(event) {
        this.ontransitionend(event);
    };
    var dashedVendorProperties = {
        "-webkit-transform": "transform",
        "-moz-transform": "transform",
        "-o-transform": "transform"
    };
    Item.prototype.ontransitionend = function(event) {
        if (event.target === this.element) {
            var _transition = this._transn, propertyName = dashedVendorProperties[event.propertyName] || event.propertyName;
            if (delete _transition.ingProperties[propertyName], isEmptyObj(_transition.ingProperties) && this.disableTransition(), 
            propertyName in _transition.clean && (this.element.style[event.propertyName] = "", 
            delete _transition.clean[propertyName]), propertyName in _transition.onEnd) {
                var onTransitionEnd = _transition.onEnd[propertyName];
                onTransitionEnd.call(this), delete _transition.onEnd[propertyName];
            }
            this.emitEvent("transitionEnd", [ this ]);
        }
    }, Item.prototype.disableTransition = function() {
        this.removeTransitionStyles(), this.element.removeEventListener(transitionEndEvent, this, !1), 
        this.isTransitioning = !1;
    }, Item.prototype._removeStyles = function(style) {
        var cleanStyle = {};
        for (var prop in style) cleanStyle[prop] = "";
        this.css(cleanStyle);
    };
    var cleanTransitionStyle = {
        transitionProperty: "",
        transitionDuration: ""
    };
    return Item.prototype.removeTransitionStyles = function() {
        this.css(cleanTransitionStyle);
    }, Item.prototype.removeElem = function() {
        this.element.parentNode.removeChild(this.element), this.css({
            display: ""
        }), this.emitEvent("remove", [ this ]);
    }, Item.prototype.remove = function() {
        if (!transitionProperty || !parseFloat(this.layout.options.transitionDuration)) return void this.removeElem();
        var _this = this;
        this.once("transitionEnd", function() {
            _this.removeElem();
        }), this.hide();
    }, Item.prototype.reveal = function() {
        delete this.isHidden, this.css({
            display: ""
        });
        var options = this.layout.options, onTransitionEnd = {}, transitionEndProperty = this.getHideRevealTransitionEndProperty("visibleStyle");
        onTransitionEnd[transitionEndProperty] = this.onRevealTransitionEnd, this.transition({
            from: options.hiddenStyle,
            to: options.visibleStyle,
            isCleaning: !0,
            onTransitionEnd: onTransitionEnd
        });
    }, Item.prototype.onRevealTransitionEnd = function() {
        this.isHidden || this.emitEvent("reveal");
    }, Item.prototype.getHideRevealTransitionEndProperty = function(styleProperty) {
        var optionStyle = this.layout.options[styleProperty];
        if (optionStyle.opacity) return "opacity";
        for (var prop in optionStyle) return prop;
    }, Item.prototype.hide = function() {
        this.isHidden = !0, this.css({
            display: ""
        });
        var options = this.layout.options, onTransitionEnd = {}, transitionEndProperty = this.getHideRevealTransitionEndProperty("hiddenStyle");
        onTransitionEnd[transitionEndProperty] = this.onHideTransitionEnd, this.transition({
            from: options.visibleStyle,
            to: options.hiddenStyle,
            isCleaning: !0,
            onTransitionEnd: onTransitionEnd
        });
    }, Item.prototype.onHideTransitionEnd = function() {
        this.isHidden && (this.css({
            display: "none"
        }), this.emitEvent("hide"));
    }, Item.prototype.destroy = function() {
        this.css({
            position: "",
            left: "",
            right: "",
            top: "",
            bottom: "",
            transition: "",
            transform: ""
        });
    }, Item;
}), /*!
 * Outlayer v1.4.2
 * the brains and guts of a layout library
 * MIT license
 */
function(window, factory) {
    "function" == typeof define && define.amd ? define("outlayer/outlayer", [ "eventie/eventie", "eventEmitter/EventEmitter", "get-size/get-size", "fizzy-ui-utils/utils", "./item" ], function(eventie, EventEmitter, getSize, utils, Item) {
        return factory(window, eventie, EventEmitter, getSize, utils, Item);
    }) : "object" == typeof exports ? module.exports = factory(window, require("eventie"), require("wolfy87-eventemitter"), require("get-size"), require("fizzy-ui-utils"), require("./item")) : window.Outlayer = factory(window, window.eventie, window.EventEmitter, window.getSize, window.fizzyUIUtils, window.Outlayer.Item);
}(window, function(window, eventie, EventEmitter, getSize, utils, Item) {
    function Outlayer(element, options) {
        var queryElement = utils.getQueryElement(element);
        if (!queryElement) return void (console && console.error("Bad element for " + this.constructor.namespace + ": " + (queryElement || element)));
        this.element = queryElement, jQuery && (this.$element = jQuery(this.element)), this.options = utils.extend({}, this.constructor.defaults), 
        this.option(options);
        var id = ++GUID;
        this.element.outlayerGUID = id, instances[id] = this, this._create(), this.options.isInitLayout && this.layout();
    }
    var console = window.console, jQuery = window.jQuery, noop = function() {}, GUID = 0, instances = {};
    return Outlayer.namespace = "outlayer", Outlayer.Item = Item, Outlayer.defaults = {
        containerStyle: {
            position: "relative"
        },
        isInitLayout: !0,
        isOriginLeft: !0,
        isOriginTop: !0,
        isResizeBound: !0,
        isResizingContainer: !0,
        transitionDuration: "0.4s",
        hiddenStyle: {
            opacity: 0,
            transform: "scale(0.001)"
        },
        visibleStyle: {
            opacity: 1,
            transform: "scale(1)"
        }
    }, utils.extend(Outlayer.prototype, EventEmitter.prototype), Outlayer.prototype.option = function(opts) {
        utils.extend(this.options, opts);
    }, Outlayer.prototype._create = function() {
        this.reloadItems(), this.stamps = [], this.stamp(this.options.stamp), utils.extend(this.element.style, this.options.containerStyle), 
        this.options.isResizeBound && this.bindResize();
    }, Outlayer.prototype.reloadItems = function() {
        this.items = this._itemize(this.element.children);
    }, Outlayer.prototype._itemize = function(elems) {
        for (var itemElems = this._filterFindItemElements(elems), Item = this.constructor.Item, items = [], i = 0, len = itemElems.length; len > i; i++) {
            var elem = itemElems[i], item = new Item(elem, this);
            items.push(item);
        }
        return items;
    }, Outlayer.prototype._filterFindItemElements = function(elems) {
        return utils.filterFindElements(elems, this.options.itemSelector);
    }, Outlayer.prototype.getItemElements = function() {
        for (var elems = [], i = 0, len = this.items.length; len > i; i++) elems.push(this.items[i].element);
        return elems;
    }, Outlayer.prototype.layout = function() {
        this._resetLayout(), this._manageStamps();
        var isInstant = void 0 !== this.options.isLayoutInstant ? this.options.isLayoutInstant : !this._isLayoutInited;
        this.layoutItems(this.items, isInstant), this._isLayoutInited = !0;
    }, Outlayer.prototype._init = Outlayer.prototype.layout, Outlayer.prototype._resetLayout = function() {
        this.getSize();
    }, Outlayer.prototype.getSize = function() {
        this.size = getSize(this.element);
    }, Outlayer.prototype._getMeasurement = function(measurement, size) {
        var elem, option = this.options[measurement];
        option ? ("string" == typeof option ? elem = this.element.querySelector(option) : utils.isElement(option) && (elem = option), 
        this[measurement] = elem ? getSize(elem)[size] : option) : this[measurement] = 0;
    }, Outlayer.prototype.layoutItems = function(items, isInstant) {
        items = this._getItemsForLayout(items), this._layoutItems(items, isInstant), this._postLayout();
    }, Outlayer.prototype._getItemsForLayout = function(items) {
        for (var layoutItems = [], i = 0, len = items.length; len > i; i++) {
            var item = items[i];
            item.isIgnored || layoutItems.push(item);
        }
        return layoutItems;
    }, Outlayer.prototype._layoutItems = function(items, isInstant) {
        if (this._emitCompleteOnItems("layout", items), items && items.length) {
            for (var queue = [], i = 0, len = items.length; len > i; i++) {
                var item = items[i], position = this._getItemLayoutPosition(item);
                position.item = item, position.isInstant = isInstant || item.isLayoutInstant, queue.push(position);
            }
            this._processLayoutQueue(queue);
        }
    }, Outlayer.prototype._getItemLayoutPosition = function() {
        return {
            x: 0,
            y: 0
        };
    }, Outlayer.prototype._processLayoutQueue = function(queue) {
        for (var i = 0, len = queue.length; len > i; i++) {
            var obj = queue[i];
            this._positionItem(obj.item, obj.x, obj.y, obj.isInstant);
        }
    }, Outlayer.prototype._positionItem = function(item, x, y, isInstant) {
        isInstant ? item.goTo(x, y) : item.moveTo(x, y);
    }, Outlayer.prototype._postLayout = function() {
        this.resizeContainer();
    }, Outlayer.prototype.resizeContainer = function() {
        if (this.options.isResizingContainer) {
            var size = this._getContainerSize();
            size && (this._setContainerMeasure(size.width, !0), this._setContainerMeasure(size.height, !1));
        }
    }, Outlayer.prototype._getContainerSize = noop, Outlayer.prototype._setContainerMeasure = function(measure, isWidth) {
        if (void 0 !== measure) {
            var elemSize = this.size;
            elemSize.isBorderBox && (measure += isWidth ? elemSize.paddingLeft + elemSize.paddingRight + elemSize.borderLeftWidth + elemSize.borderRightWidth : elemSize.paddingBottom + elemSize.paddingTop + elemSize.borderTopWidth + elemSize.borderBottomWidth), 
            measure = Math.max(measure, 0), this.element.style[isWidth ? "width" : "height"] = measure + "px";
        }
    }, Outlayer.prototype._emitCompleteOnItems = function(eventName, items) {
        function onComplete() {
            _this.dispatchEvent(eventName + "Complete", null, [ items ]);
        }
        function tick() {
            doneCount++, doneCount === count && onComplete();
        }
        var _this = this, count = items.length;
        if (!items || !count) return void onComplete();
        for (var doneCount = 0, i = 0, len = items.length; len > i; i++) {
            var item = items[i];
            item.once(eventName, tick);
        }
    }, Outlayer.prototype.dispatchEvent = function(type, event, args) {
        var emitArgs = event ? [ event ].concat(args) : args;
        if (this.emitEvent(type, emitArgs), jQuery) if (this.$element = this.$element || jQuery(this.element), 
        event) {
            var $event = jQuery.Event(event);
            $event.type = type, this.$element.trigger($event, args);
        } else this.$element.trigger(type, args);
    }, Outlayer.prototype.ignore = function(elem) {
        var item = this.getItem(elem);
        item && (item.isIgnored = !0);
    }, Outlayer.prototype.unignore = function(elem) {
        var item = this.getItem(elem);
        item && delete item.isIgnored;
    }, Outlayer.prototype.stamp = function(elems) {
        if (elems = this._find(elems)) {
            this.stamps = this.stamps.concat(elems);
            for (var i = 0, len = elems.length; len > i; i++) {
                var elem = elems[i];
                this.ignore(elem);
            }
        }
    }, Outlayer.prototype.unstamp = function(elems) {
        if (elems = this._find(elems)) for (var i = 0, len = elems.length; len > i; i++) {
            var elem = elems[i];
            utils.removeFrom(this.stamps, elem), this.unignore(elem);
        }
    }, Outlayer.prototype._find = function(elems) {
        return elems ? ("string" == typeof elems && (elems = this.element.querySelectorAll(elems)), 
        elems = utils.makeArray(elems)) : void 0;
    }, Outlayer.prototype._manageStamps = function() {
        if (this.stamps && this.stamps.length) {
            this._getBoundingRect();
            for (var i = 0, len = this.stamps.length; len > i; i++) {
                var stamp = this.stamps[i];
                this._manageStamp(stamp);
            }
        }
    }, Outlayer.prototype._getBoundingRect = function() {
        var boundingRect = this.element.getBoundingClientRect(), size = this.size;
        this._boundingRect = {
            left: boundingRect.left + size.paddingLeft + size.borderLeftWidth,
            top: boundingRect.top + size.paddingTop + size.borderTopWidth,
            right: boundingRect.right - (size.paddingRight + size.borderRightWidth),
            bottom: boundingRect.bottom - (size.paddingBottom + size.borderBottomWidth)
        };
    }, Outlayer.prototype._manageStamp = noop, Outlayer.prototype._getElementOffset = function(elem) {
        var boundingRect = elem.getBoundingClientRect(), thisRect = this._boundingRect, size = getSize(elem), offset = {
            left: boundingRect.left - thisRect.left - size.marginLeft,
            top: boundingRect.top - thisRect.top - size.marginTop,
            right: thisRect.right - boundingRect.right - size.marginRight,
            bottom: thisRect.bottom - boundingRect.bottom - size.marginBottom
        };
        return offset;
    }, Outlayer.prototype.handleEvent = function(event) {
        var method = "on" + event.type;
        this[method] && this[method](event);
    }, Outlayer.prototype.bindResize = function() {
        this.isResizeBound || (eventie.bind(window, "resize", this), this.isResizeBound = !0);
    }, Outlayer.prototype.unbindResize = function() {
        this.isResizeBound && eventie.unbind(window, "resize", this), this.isResizeBound = !1;
    }, Outlayer.prototype.onresize = function() {
        function delayed() {
            _this.resize(), delete _this.resizeTimeout;
        }
        this.resizeTimeout && clearTimeout(this.resizeTimeout);
        var _this = this;
        this.resizeTimeout = setTimeout(delayed, 100);
    }, Outlayer.prototype.resize = function() {
        this.isResizeBound && this.needsResizeLayout() && this.layout();
    }, Outlayer.prototype.needsResizeLayout = function() {
        var size = getSize(this.element), hasSizes = this.size && size;
        return hasSizes && size.innerWidth !== this.size.innerWidth;
    }, Outlayer.prototype.addItems = function(elems) {
        var items = this._itemize(elems);
        return items.length && (this.items = this.items.concat(items)), items;
    }, Outlayer.prototype.appended = function(elems) {
        var items = this.addItems(elems);
        items.length && (this.layoutItems(items, !0), this.reveal(items));
    }, Outlayer.prototype.prepended = function(elems) {
        var items = this._itemize(elems);
        if (items.length) {
            var previousItems = this.items.slice(0);
            this.items = items.concat(previousItems), this._resetLayout(), this._manageStamps(), 
            this.layoutItems(items, !0), this.reveal(items), this.layoutItems(previousItems);
        }
    }, Outlayer.prototype.reveal = function(items) {
        this._emitCompleteOnItems("reveal", items);
        for (var len = items && items.length, i = 0; len && len > i; i++) {
            var item = items[i];
            item.reveal();
        }
    }, Outlayer.prototype.hide = function(items) {
        this._emitCompleteOnItems("hide", items);
        for (var len = items && items.length, i = 0; len && len > i; i++) {
            var item = items[i];
            item.hide();
        }
    }, Outlayer.prototype.revealItemElements = function(elems) {
        var items = this.getItems(elems);
        this.reveal(items);
    }, Outlayer.prototype.hideItemElements = function(elems) {
        var items = this.getItems(elems);
        this.hide(items);
    }, Outlayer.prototype.getItem = function(elem) {
        for (var i = 0, len = this.items.length; len > i; i++) {
            var item = this.items[i];
            if (item.element === elem) return item;
        }
    }, Outlayer.prototype.getItems = function(elems) {
        elems = utils.makeArray(elems);
        for (var items = [], i = 0, len = elems.length; len > i; i++) {
            var elem = elems[i], item = this.getItem(elem);
            item && items.push(item);
        }
        return items;
    }, Outlayer.prototype.remove = function(elems) {
        var removeItems = this.getItems(elems);
        if (this._emitCompleteOnItems("remove", removeItems), removeItems && removeItems.length) for (var i = 0, len = removeItems.length; len > i; i++) {
            var item = removeItems[i];
            item.remove(), utils.removeFrom(this.items, item);
        }
    }, Outlayer.prototype.destroy = function() {
        var style = this.element.style;
        style.height = "", style.position = "", style.width = "";
        for (var i = 0, len = this.items.length; len > i; i++) {
            var item = this.items[i];
            item.destroy();
        }
        this.unbindResize();
        var id = this.element.outlayerGUID;
        delete instances[id], delete this.element.outlayerGUID, jQuery && jQuery.removeData(this.element, this.constructor.namespace);
    }, Outlayer.data = function(elem) {
        elem = utils.getQueryElement(elem);
        var id = elem && elem.outlayerGUID;
        return id && instances[id];
    }, Outlayer.create = function(namespace, options) {
        function Layout() {
            Outlayer.apply(this, arguments);
        }
        return Object.create ? Layout.prototype = Object.create(Outlayer.prototype) : utils.extend(Layout.prototype, Outlayer.prototype), 
        Layout.prototype.constructor = Layout, Layout.defaults = utils.extend({}, Outlayer.defaults), 
        utils.extend(Layout.defaults, options), Layout.prototype.settings = {}, Layout.namespace = namespace, 
        Layout.data = Outlayer.data, Layout.Item = function() {
            Item.apply(this, arguments);
        }, Layout.Item.prototype = new Item(), utils.htmlInit(Layout, namespace), jQuery && jQuery.bridget && jQuery.bridget(namespace, Layout), 
        Layout;
    }, Outlayer.Item = Item, Outlayer;
}), /*!
 * Masonry v3.3.2
 * Cascading grid layout library
 * http://masonry.desandro.com
 * MIT License
 * by David DeSandro
 */
function(window, factory) {
    "function" == typeof define && define.amd ? define([ "outlayer/outlayer", "get-size/get-size", "fizzy-ui-utils/utils" ], factory) : "object" == typeof exports ? module.exports = factory(require("outlayer"), require("get-size"), require("fizzy-ui-utils")) : window.Masonry = factory(window.Outlayer, window.getSize, window.fizzyUIUtils);
}(window, function(Outlayer, getSize, utils) {
    var Masonry = Outlayer.create("masonry");
    return Masonry.prototype._resetLayout = function() {
        this.getSize(), this._getMeasurement("columnWidth", "outerWidth"), this._getMeasurement("gutter", "outerWidth"), 
        this.measureColumns();
        var i = this.cols;
        for (this.colYs = []; i--; ) this.colYs.push(0);
        this.maxY = 0;
    }, Masonry.prototype.measureColumns = function() {
        if (this.getContainerWidth(), !this.columnWidth) {
            var firstItem = this.items[0], firstItemElem = firstItem && firstItem.element;
            this.columnWidth = firstItemElem && getSize(firstItemElem).outerWidth || this.containerWidth;
        }
        var columnWidth = this.columnWidth += this.gutter, containerWidth = this.containerWidth + this.gutter, cols = containerWidth / columnWidth, excess = columnWidth - containerWidth % columnWidth, mathMethod = excess && 1 > excess ? "round" : "floor";
        cols = Math[mathMethod](cols), this.cols = Math.max(cols, 1);
    }, Masonry.prototype.getContainerWidth = function() {
        var container = this.options.isFitWidth ? this.element.parentNode : this.element, size = getSize(container);
        this.containerWidth = size && size.innerWidth;
    }, Masonry.prototype._getItemLayoutPosition = function(item) {
        item.getSize();
        var remainder = item.size.outerWidth % this.columnWidth, mathMethod = remainder && 1 > remainder ? "round" : "ceil", colSpan = Math[mathMethod](item.size.outerWidth / this.columnWidth);
        colSpan = Math.min(colSpan, this.cols);
        for (var colGroup = this._getColGroup(colSpan), minimumY = Math.min.apply(Math, colGroup), shortColIndex = utils.indexOf(colGroup, minimumY), position = {
            x: this.columnWidth * shortColIndex,
            y: minimumY
        }, setHeight = minimumY + item.size.outerHeight, setSpan = this.cols + 1 - colGroup.length, i = 0; setSpan > i; i++) this.colYs[shortColIndex + i] = setHeight;
        return position;
    }, Masonry.prototype._getColGroup = function(colSpan) {
        if (2 > colSpan) return this.colYs;
        for (var colGroup = [], groupCount = this.cols + 1 - colSpan, i = 0; groupCount > i; i++) {
            var groupColYs = this.colYs.slice(i, i + colSpan);
            colGroup[i] = Math.max.apply(Math, groupColYs);
        }
        return colGroup;
    }, Masonry.prototype._manageStamp = function(stamp) {
        var stampSize = getSize(stamp), offset = this._getElementOffset(stamp), firstX = this.options.isOriginLeft ? offset.left : offset.right, lastX = firstX + stampSize.outerWidth, firstCol = Math.floor(firstX / this.columnWidth);
        firstCol = Math.max(0, firstCol);
        var lastCol = Math.floor(lastX / this.columnWidth);
        lastCol -= lastX % this.columnWidth ? 0 : 1, lastCol = Math.min(this.cols - 1, lastCol);
        for (var stampMaxY = (this.options.isOriginTop ? offset.top : offset.bottom) + stampSize.outerHeight, i = firstCol; lastCol >= i; i++) this.colYs[i] = Math.max(stampMaxY, this.colYs[i]);
    }, Masonry.prototype._getContainerSize = function() {
        this.maxY = Math.max.apply(Math, this.colYs);
        var size = {
            height: this.maxY
        };
        return this.options.isFitWidth && (size.width = this._getContainerFitWidth()), size;
    }, Masonry.prototype._getContainerFitWidth = function() {
        for (var unusedCols = 0, i = this.cols; --i && 0 === this.colYs[i]; ) unusedCols++;
        return (this.cols - unusedCols) * this.columnWidth - this.gutter;
    }, Masonry.prototype.needsResizeLayout = function() {
        var previousWidth = this.containerWidth;
        return this.getContainerWidth(), previousWidth !== this.containerWidth;
    }, Masonry;
}), function($) {
    "use strict";
    function Featherlight($content, config) {
        if (!(this instanceof Featherlight)) {
            var fl = new Featherlight($content, config);
            return fl.open(), fl;
        }
        this.id = Featherlight.id++, this.setup($content, config), this.chainCallbacks(Featherlight._callbackChain);
    }
    if ("undefined" == typeof $) return void ("console" in window && window.console.info("Too much lightness, Featherlight needs jQuery."));
    var opened = [], pruneOpened = function(remove) {
        return opened = $.grep(opened, function(fl) {
            return fl !== remove && fl.$instance.closest("body").length > 0;
        });
    }, structure = function(obj, prefix) {
        var result = {}, regex = new RegExp("^" + prefix + "([A-Z])(.*)");
        for (var key in obj) {
            var match = key.match(regex);
            if (match) {
                var dasherized = (match[1] + match[2].replace(/([A-Z])/g, "-$1")).toLowerCase();
                result[dasherized] = obj[key];
            }
        }
        return result;
    }, eventMap = {
        keyup: "onKeyUp",
        resize: "onResize"
    }, globalEventHandler = function(event) {
        $.each(Featherlight.opened().reverse(), function() {
            return event.isDefaultPrevented() || !1 !== this[eventMap[event.type]](event) ? void 0 : (event.preventDefault(), 
            event.stopPropagation(), !1);
        });
    }, toggleGlobalEvents = function(set) {
        if (set !== Featherlight._globalHandlerInstalled) {
            Featherlight._globalHandlerInstalled = set;
            var events = $.map(eventMap, function(_, name) {
                return name + "." + Featherlight.prototype.namespace;
            }).join(" ");
            $(window)[set ? "on" : "off"](events, globalEventHandler);
        }
    };
    Featherlight.prototype = {
        constructor: Featherlight,
        namespace: "featherlight",
        targetAttr: "data-featherlight",
        variant: null,
        resetCss: !1,
        background: null,
        openTrigger: "click",
        closeTrigger: "click",
        filter: null,
        root: "body",
        openSpeed: 250,
        closeSpeed: 250,
        closeOnClick: "background",
        closeOnEsc: !0,
        closeIcon: "&#10005;",
        loading: "",
        persist: !1,
        otherClose: null,
        beforeOpen: $.noop,
        beforeContent: $.noop,
        beforeClose: $.noop,
        afterOpen: $.noop,
        afterContent: $.noop,
        afterClose: $.noop,
        onKeyUp: $.noop,
        onResize: $.noop,
        type: null,
        contentFilters: [ "jquery", "image", "html", "ajax", "iframe", "text" ],
        setup: function(target, config) {
            "object" != typeof target || target instanceof $ != !1 || config || (config = target, 
            target = void 0);
            var self = $.extend(this, config, {
                target: target
            }), css = self.resetCss ? self.namespace + "-reset" : self.namespace, $background = $(self.background || [ '<div class="' + css + "-loading " + css + '">', '<div class="' + css + '-content">', '<span class="' + css + "-close-icon " + self.namespace + '-close">', self.closeIcon, "</span>", '<div class="' + self.namespace + '-inner">' + self.loading + "</div>", "</div>", "</div>" ].join("")), closeButtonSelector = "." + self.namespace + "-close" + (self.otherClose ? "," + self.otherClose : "");
            return self.$instance = $background.clone().addClass(self.variant), self.$instance.on(self.closeTrigger + "." + self.namespace, function(event) {
                var $target = $(event.target);
                ("background" === self.closeOnClick && $target.is("." + self.namespace) || "anywhere" === self.closeOnClick || $target.closest(closeButtonSelector).length) && (self.close(event), 
                event.preventDefault());
            }), this;
        },
        getContent: function() {
            if (this.persist !== !1 && this.$content) return this.$content;
            var self = this, filters = this.constructor.contentFilters, readTargetAttr = function(name) {
                return self.$currentTarget && self.$currentTarget.attr(name);
            }, targetValue = readTargetAttr(self.targetAttr), data = self.target || targetValue || "", filter = filters[self.type];
            if (!filter && data in filters && (filter = filters[data], data = self.target && targetValue), 
            data = data || readTargetAttr("href") || "", !filter) for (var filterName in filters) self[filterName] && (filter = filters[filterName], 
            data = self[filterName]);
            if (!filter) {
                var target = data;
                if (data = null, $.each(self.contentFilters, function() {
                    return filter = filters[this], filter.test && (data = filter.test(target)), !data && filter.regex && target.match && target.match(filter.regex) && (data = target), 
                    !data;
                }), !data) return "console" in window && window.console.error("Featherlight: no content filter found " + (target ? ' for "' + target + '"' : " (no target specified)")), 
                !1;
            }
            return filter.process.call(self, data);
        },
        setContent: function($content) {
            var self = this;
            return ($content.is("iframe") || $("iframe", $content).length > 0) && self.$instance.addClass(self.namespace + "-iframe"), 
            self.$instance.removeClass(self.namespace + "-loading"), self.$instance.find("." + self.namespace + "-inner").not($content).slice(1).remove().end().replaceWith($.contains(self.$instance[0], $content[0]) ? "" : $content), 
            self.$content = $content.addClass(self.namespace + "-inner"), self;
        },
        open: function(event) {
            var self = this;
            if (self.$instance.hide().appendTo(self.root), !(event && event.isDefaultPrevented() || self.beforeOpen(event) === !1)) {
                event && event.preventDefault();
                var $content = self.getContent();
                if ($content) return opened.push(self), toggleGlobalEvents(!0), self.$instance.fadeIn(self.openSpeed), 
                self.beforeContent(event), $.when($content).always(function($content) {
                    self.setContent($content), self.afterContent(event);
                }).then(self.$instance.promise()).done(function() {
                    self.afterOpen(event);
                });
            }
            return self.$instance.detach(), $.Deferred().reject().promise();
        },
        close: function(event) {
            var self = this, deferred = $.Deferred();
            return self.beforeClose(event) === !1 ? deferred.reject() : (0 === pruneOpened(self).length && toggleGlobalEvents(!1), 
            self.$instance.fadeOut(self.closeSpeed, function() {
                self.$instance.detach(), self.afterClose(event), deferred.resolve();
            })), deferred.promise();
        },
        chainCallbacks: function(chain) {
            for (var name in chain) this[name] = $.proxy(chain[name], this, $.proxy(this[name], this));
        }
    }, $.extend(Featherlight, {
        id: 0,
        autoBind: "[data-featherlight]",
        defaults: Featherlight.prototype,
        contentFilters: {
            jquery: {
                regex: /^[#.]\w/,
                test: function(elem) {
                    return elem instanceof $ && elem;
                },
                process: function(elem) {
                    return this.persist !== !1 ? $(elem) : $(elem).clone(!0);
                }
            },
            image: {
                regex: /\.(png|jpg|jpeg|gif|tiff|bmp|svg)(\?\S*)?$/i,
                process: function(url) {
                    var self = this, deferred = $.Deferred(), img = new Image(), $img = $('<img src="' + url + '" alt="" class="' + self.namespace + '-image" />');
                    return img.onload = function() {
                        $img.naturalWidth = img.width, $img.naturalHeight = img.height, deferred.resolve($img);
                    }, img.onerror = function() {
                        deferred.reject($img);
                    }, img.src = url, deferred.promise();
                }
            },
            html: {
                regex: /^\s*<[\w!][^<]*>/,
                process: function(html) {
                    return $(html);
                }
            },
            ajax: {
                regex: /./,
                process: function(url) {
                    var deferred = $.Deferred(), $container = $("<div></div>").load(url, function(response, status) {
                        "error" !== status && deferred.resolve($container.contents()), deferred.fail();
                    });
                    return deferred.promise();
                }
            },
            iframe: {
                process: function(url) {
                    var deferred = new $.Deferred(), $content = $("<iframe/>").hide().attr("src", url).css(structure(this, "iframe")).on("load", function() {
                        deferred.resolve($content.show());
                    }).appendTo(this.$instance.find("." + this.namespace + "-content"));
                    return deferred.promise();
                }
            },
            text: {
                process: function(text) {
                    return $("<div>", {
                        text: text
                    });
                }
            }
        },
        functionAttributes: [ "beforeOpen", "afterOpen", "beforeContent", "afterContent", "beforeClose", "afterClose" ],
        readElementConfig: function(element, namespace) {
            var Klass = this, regexp = new RegExp("^data-" + namespace + "-(.*)"), config = {};
            return element && element.attributes && $.each(element.attributes, function() {
                var match = this.name.match(regexp);
                if (match) {
                    var val = this.value, name = $.camelCase(match[1]);
                    if ($.inArray(name, Klass.functionAttributes) >= 0) val = new Function(val); else try {
                        val = $.parseJSON(val);
                    } catch (e) {}
                    config[name] = val;
                }
            }), config;
        },
        extend: function(child, defaults) {
            var Ctor = function() {
                this.constructor = child;
            };
            return Ctor.prototype = this.prototype, child.prototype = new Ctor(), child.__super__ = this.prototype, 
            $.extend(child, this, defaults), child.defaults = child.prototype, child;
        },
        attach: function($source, $content, config) {
            var Klass = this;
            "object" != typeof $content || $content instanceof $ != !1 || config || (config = $content, 
            $content = void 0), config = $.extend({}, config);
            var sharedPersist, namespace = config.namespace || Klass.defaults.namespace, tempConfig = $.extend({}, Klass.defaults, Klass.readElementConfig($source[0], namespace), config);
            return $source.on(tempConfig.openTrigger + "." + tempConfig.namespace, tempConfig.filter, function(event) {
                var elemConfig = $.extend({
                    $source: $source,
                    $currentTarget: $(this)
                }, Klass.readElementConfig($source[0], tempConfig.namespace), Klass.readElementConfig(this, tempConfig.namespace), config), fl = sharedPersist || $(this).data("featherlight-persisted") || new Klass($content, elemConfig);
                "shared" === fl.persist ? sharedPersist = fl : fl.persist !== !1 && $(this).data("featherlight-persisted", fl), 
                elemConfig.$currentTarget.blur(), fl.open(event);
            }), $source;
        },
        current: function() {
            var all = this.opened();
            return all[all.length - 1] || null;
        },
        opened: function() {
            var klass = this;
            return pruneOpened(), $.grep(opened, function(fl) {
                return fl instanceof klass;
            });
        },
        close: function(event) {
            var cur = this.current();
            return cur ? cur.close(event) : void 0;
        },
        _onReady: function() {
            var Klass = this;
            Klass.autoBind && ($(Klass.autoBind).each(function() {
                Klass.attach($(this));
            }), $(document).on("click", Klass.autoBind, function(evt) {
                evt.isDefaultPrevented() || "featherlight" === evt.namespace || (evt.preventDefault(), 
                Klass.attach($(evt.currentTarget)), $(evt.target).trigger("click.featherlight"));
            }));
        },
        _callbackChain: {
            onKeyUp: function(_super, event) {
                return 27 === event.keyCode ? (this.closeOnEsc && $.featherlight.close(event), !1) : _super(event);
            },
            onResize: function(_super, event) {
                if (this.$content.naturalWidth) {
                    var w = this.$content.naturalWidth, h = this.$content.naturalHeight;
                    this.$content.css("width", "").css("height", "");
                    var ratio = Math.max(w / parseInt(this.$content.parent().css("width"), 10), h / parseInt(this.$content.parent().css("height"), 10));
                    ratio > 1 && this.$content.css("width", "" + w / ratio + "px").css("height", "" + h / ratio + "px");
                }
                return _super(event);
            },
            afterContent: function(_super, event) {
                var r = _super(event);
                return this.onResize(event), r;
            }
        }
    }), $.featherlight = Featherlight, $.fn.featherlight = function($content, config) {
        return Featherlight.attach(this, $content, config);
    }, $(document).ready(function() {
        Featherlight._onReady();
    });
}(jQuery), function($) {
    "use strict";
    function FeatherlightGallery($source, config) {
        if (!(this instanceof FeatherlightGallery)) {
            var flg = new FeatherlightGallery($.extend({
                $source: $source,
                $currentTarget: $source.first()
            }, config));
            return flg.open(), flg;
        }
        $.featherlight.apply(this, arguments), this.chainCallbacks(callbackChain);
    }
    var warn = function(m) {
        window.console && window.console.warn && window.console.warn("FeatherlightGallery: " + m);
    };
    if ("undefined" == typeof $) return warn("Too much lightness, Featherlight needs jQuery.");
    if (!$.featherlight) return warn("Load the featherlight plugin before the gallery plugin");
    var isTouchAware = "ontouchstart" in window || window.DocumentTouch && document instanceof DocumentTouch, jQueryConstructor = $.event && $.event.special.swipeleft && $, hammerConstructor = window.Hammer && function($el) {
        var mc = new window.Hammer.Manager($el[0]);
        return mc.add(new window.Hammer.Swipe()), mc;
    }, swipeAwareConstructor = isTouchAware && (jQueryConstructor || hammerConstructor);
    isTouchAware && !swipeAwareConstructor && warn("No compatible swipe library detected; one must be included before featherlightGallery for swipe motions to navigate the galleries.");
    var callbackChain = {
        afterClose: function(_super, event) {
            var self = this;
            return self.$instance.off("next." + self.namespace + " previous." + self.namespace), 
            self._swiper && (self._swiper.off("swipeleft", self._swipeleft).off("swiperight", self._swiperight), 
            self._swiper = null), _super(event);
        },
        beforeOpen: function(_super, event) {
            var self = this;
            return self.$instance.on("next." + self.namespace + " previous." + self.namespace, function(event) {
                var offset = "next" === event.type ? 1 : -1;
                self.navigateTo(self.currentNavigation() + offset);
            }), swipeAwareConstructor ? self._swiper = swipeAwareConstructor(self.$instance).on("swipeleft", self._swipeleft = function() {
                self.$instance.trigger("next");
            }).on("swiperight", self._swiperight = function() {
                self.$instance.trigger("previous");
            }) : self.$instance.find("." + self.namespace + "-content").append(self.createNavigation("previous")).append(self.createNavigation("next")), 
            _super(event);
        },
        onKeyUp: function(_super, event) {
            var dir = {
                37: "previous",
                39: "next"
            }[event.keyCode];
            return dir ? (this.$instance.trigger(dir), !1) : _super(event);
        }
    };
    $.featherlight.extend(FeatherlightGallery, {
        autoBind: "[data-featherlight-gallery]"
    }), $.extend(FeatherlightGallery.prototype, {
        previousIcon: "&#9664;",
        nextIcon: "&#9654;",
        galleryFadeIn: 100,
        galleryFadeOut: 300,
        slides: function() {
            return this.filter ? this.$source.find(this.filter) : this.$source;
        },
        images: function() {
            return warn("images is deprecated, please use slides instead"), this.slides();
        },
        currentNavigation: function() {
            return this.slides().index(this.$currentTarget);
        },
        navigateTo: function(index) {
            var self = this, source = self.slides(), len = source.length, $inner = self.$instance.find("." + self.namespace + "-inner");
            return index = (index % len + len) % len, self.$currentTarget = source.eq(index), 
            self.beforeContent(), $.when(self.getContent(), $inner.fadeTo(self.galleryFadeOut, .2)).always(function($newContent) {
                self.setContent($newContent), self.afterContent(), $newContent.fadeTo(self.galleryFadeIn, 1);
            });
        },
        createNavigation: function(target) {
            var self = this;
            return $('<span title="' + target + '" class="' + this.namespace + "-" + target + '"><span>' + this[target + "Icon"] + "</span></span>").click(function() {
                $(this).trigger(target + "." + self.namespace);
            });
        }
    }), $.featherlightGallery = FeatherlightGallery, $.fn.featherlightGallery = function(config) {
        return FeatherlightGallery.attach(this, config);
    }, $(document).ready(function() {
        FeatherlightGallery._onReady();
    });
}(jQuery), +function($) {
    "use strict";
    function Plugin(option) {
        return this.each(function() {
            var $this = $(this), data = $this.data("bs.alert");
            data || $this.data("bs.alert", data = new Alert(this)), "string" == typeof option && data[option].call($this);
        });
    }
    var dismiss = '[data-dismiss="alert"]', Alert = function(el) {
        $(el).on("click", dismiss, this.close);
    };
    Alert.VERSION = "3.3.5", Alert.TRANSITION_DURATION = 150, Alert.prototype.close = function(e) {
        function removeElement() {
            $parent.detach().trigger("closed.bs.alert").remove();
        }
        var $this = $(this), selector = $this.attr("data-target");
        selector || (selector = $this.attr("href"), selector = selector && selector.replace(/.*(?=#[^\s]*$)/, ""));
        var $parent = $(selector);
        e && e.preventDefault(), $parent.length || ($parent = $this.closest(".alert")), 
        $parent.trigger(e = $.Event("close.bs.alert")), e.isDefaultPrevented() || ($parent.removeClass("in"), 
        $.support.transition && $parent.hasClass("fade") ? $parent.one("bsTransitionEnd", removeElement).emulateTransitionEnd(Alert.TRANSITION_DURATION) : removeElement());
    };
    var old = $.fn.alert;
    $.fn.alert = Plugin, $.fn.alert.Constructor = Alert, $.fn.alert.noConflict = function() {
        return $.fn.alert = old, this;
    }, $(document).on("click.bs.alert.data-api", dismiss, Alert.prototype.close);
}(jQuery), +function($) {
    "use strict";
    function Plugin(option) {
        return this.each(function() {
            var $this = $(this), data = $this.data("bs.button"), options = "object" == typeof option && option;
            data || $this.data("bs.button", data = new Button(this, options)), "toggle" == option ? data.toggle() : option && data.setState(option);
        });
    }
    var Button = function(element, options) {
        this.$element = $(element), this.options = $.extend({}, Button.DEFAULTS, options), 
        this.isLoading = !1;
    };
    Button.VERSION = "3.3.5", Button.DEFAULTS = {
        loadingText: "loading..."
    }, Button.prototype.setState = function(state) {
        var d = "disabled", $el = this.$element, val = $el.is("input") ? "val" : "html", data = $el.data();
        state += "Text", null == data.resetText && $el.data("resetText", $el[val]()), setTimeout($.proxy(function() {
            $el[val](null == data[state] ? this.options[state] : data[state]), "loadingText" == state ? (this.isLoading = !0, 
            $el.addClass(d).attr(d, d)) : this.isLoading && (this.isLoading = !1, $el.removeClass(d).removeAttr(d));
        }, this), 0);
    }, Button.prototype.toggle = function() {
        var changed = !0, $parent = this.$element.closest('[data-toggle="buttons"]');
        if ($parent.length) {
            var $input = this.$element.find("input");
            "radio" == $input.prop("type") ? ($input.prop("checked") && (changed = !1), $parent.find(".active").removeClass("active"), 
            this.$element.addClass("active")) : "checkbox" == $input.prop("type") && ($input.prop("checked") !== this.$element.hasClass("active") && (changed = !1), 
            this.$element.toggleClass("active")), $input.prop("checked", this.$element.hasClass("active")), 
            changed && $input.trigger("change");
        } else this.$element.attr("aria-pressed", !this.$element.hasClass("active")), this.$element.toggleClass("active");
    };
    var old = $.fn.button;
    $.fn.button = Plugin, $.fn.button.Constructor = Button, $.fn.button.noConflict = function() {
        return $.fn.button = old, this;
    }, $(document).on("click.bs.button.data-api", '[data-toggle^="button"]', function(e) {
        var $btn = $(e.target);
        $btn.hasClass("btn") || ($btn = $btn.closest(".btn")), Plugin.call($btn, "toggle"), 
        $(e.target).is('input[type="radio"]') || $(e.target).is('input[type="checkbox"]') || e.preventDefault();
    }).on("focus.bs.button.data-api blur.bs.button.data-api", '[data-toggle^="button"]', function(e) {
        $(e.target).closest(".btn").toggleClass("focus", /^focus(in)?$/.test(e.type));
    });
}(jQuery), +function($) {
    "use strict";
    function Plugin(option) {
        return this.each(function() {
            var $this = $(this), data = $this.data("bs.carousel"), options = $.extend({}, Carousel.DEFAULTS, $this.data(), "object" == typeof option && option), action = "string" == typeof option ? option : options.slide;
            data || $this.data("bs.carousel", data = new Carousel(this, options)), "number" == typeof option ? data.to(option) : action ? data[action]() : options.interval && data.pause().cycle();
        });
    }
    var Carousel = function(element, options) {
        this.$element = $(element), this.$indicators = this.$element.find(".carousel-indicators"), 
        this.options = options, this.paused = null, this.sliding = null, this.interval = null, 
        this.$active = null, this.$items = null, this.options.keyboard && this.$element.on("keydown.bs.carousel", $.proxy(this.keydown, this)), 
        "hover" == this.options.pause && !("ontouchstart" in document.documentElement) && this.$element.on("mouseenter.bs.carousel", $.proxy(this.pause, this)).on("mouseleave.bs.carousel", $.proxy(this.cycle, this));
    };
    Carousel.VERSION = "3.3.5", Carousel.TRANSITION_DURATION = 600, Carousel.DEFAULTS = {
        interval: 5e3,
        pause: "hover",
        wrap: !0,
        keyboard: !0
    }, Carousel.prototype.keydown = function(e) {
        if (!/input|textarea/i.test(e.target.tagName)) {
            switch (e.which) {
              case 37:
                this.prev();
                break;

              case 39:
                this.next();
                break;

              default:
                return;
            }
            e.preventDefault();
        }
    }, Carousel.prototype.cycle = function(e) {
        return e || (this.paused = !1), this.interval && clearInterval(this.interval), this.options.interval && !this.paused && (this.interval = setInterval($.proxy(this.next, this), this.options.interval)), 
        this;
    }, Carousel.prototype.getItemIndex = function(item) {
        return this.$items = item.parent().children(".item"), this.$items.index(item || this.$active);
    }, Carousel.prototype.getItemForDirection = function(direction, active) {
        var activeIndex = this.getItemIndex(active), willWrap = "prev" == direction && 0 === activeIndex || "next" == direction && activeIndex == this.$items.length - 1;
        if (willWrap && !this.options.wrap) return active;
        var delta = "prev" == direction ? -1 : 1, itemIndex = (activeIndex + delta) % this.$items.length;
        return this.$items.eq(itemIndex);
    }, Carousel.prototype.to = function(pos) {
        var that = this, activeIndex = this.getItemIndex(this.$active = this.$element.find(".item.active"));
        return pos > this.$items.length - 1 || 0 > pos ? void 0 : this.sliding ? this.$element.one("slid.bs.carousel", function() {
            that.to(pos);
        }) : activeIndex == pos ? this.pause().cycle() : this.slide(pos > activeIndex ? "next" : "prev", this.$items.eq(pos));
    }, Carousel.prototype.pause = function(e) {
        return e || (this.paused = !0), this.$element.find(".next, .prev").length && $.support.transition && (this.$element.trigger($.support.transition.end), 
        this.cycle(!0)), this.interval = clearInterval(this.interval), this;
    }, Carousel.prototype.next = function() {
        return this.sliding ? void 0 : this.slide("next");
    }, Carousel.prototype.prev = function() {
        return this.sliding ? void 0 : this.slide("prev");
    }, Carousel.prototype.slide = function(type, next) {
        var $active = this.$element.find(".item.active"), $next = next || this.getItemForDirection(type, $active), isCycling = this.interval, direction = "next" == type ? "left" : "right", that = this;
        if ($next.hasClass("active")) return this.sliding = !1;
        var relatedTarget = $next[0], slideEvent = $.Event("slide.bs.carousel", {
            relatedTarget: relatedTarget,
            direction: direction
        });
        if (this.$element.trigger(slideEvent), !slideEvent.isDefaultPrevented()) {
            if (this.sliding = !0, isCycling && this.pause(), this.$indicators.length) {
                this.$indicators.find(".active").removeClass("active");
                var $nextIndicator = $(this.$indicators.children()[this.getItemIndex($next)]);
                $nextIndicator && $nextIndicator.addClass("active");
            }
            var slidEvent = $.Event("slid.bs.carousel", {
                relatedTarget: relatedTarget,
                direction: direction
            });
            return $.support.transition && this.$element.hasClass("slide") ? ($next.addClass(type), 
            $next[0].offsetWidth, $active.addClass(direction), $next.addClass(direction), $active.one("bsTransitionEnd", function() {
                $next.removeClass([ type, direction ].join(" ")).addClass("active"), $active.removeClass([ "active", direction ].join(" ")), 
                that.sliding = !1, setTimeout(function() {
                    that.$element.trigger(slidEvent);
                }, 0);
            }).emulateTransitionEnd(Carousel.TRANSITION_DURATION)) : ($active.removeClass("active"), 
            $next.addClass("active"), this.sliding = !1, this.$element.trigger(slidEvent)), 
            isCycling && this.cycle(), this;
        }
    };
    var old = $.fn.carousel;
    $.fn.carousel = Plugin, $.fn.carousel.Constructor = Carousel, $.fn.carousel.noConflict = function() {
        return $.fn.carousel = old, this;
    };
    var clickHandler = function(e) {
        var href, $this = $(this), $target = $($this.attr("data-target") || (href = $this.attr("href")) && href.replace(/.*(?=#[^\s]+$)/, ""));
        if ($target.hasClass("carousel")) {
            var options = $.extend({}, $target.data(), $this.data()), slideIndex = $this.attr("data-slide-to");
            slideIndex && (options.interval = !1), Plugin.call($target, options), slideIndex && $target.data("bs.carousel").to(slideIndex), 
            e.preventDefault();
        }
    };
    $(document).on("click.bs.carousel.data-api", "[data-slide]", clickHandler).on("click.bs.carousel.data-api", "[data-slide-to]", clickHandler), 
    $(window).on("load", function() {
        $('[data-ride="carousel"]').each(function() {
            var $carousel = $(this);
            Plugin.call($carousel, $carousel.data());
        });
    });
}(jQuery), +function($) {
    "use strict";
    function getTargetFromTrigger($trigger) {
        var href, target = $trigger.attr("data-target") || (href = $trigger.attr("href")) && href.replace(/.*(?=#[^\s]+$)/, "");
        return $(target);
    }
    function Plugin(option) {
        return this.each(function() {
            var $this = $(this), data = $this.data("bs.collapse"), options = $.extend({}, Collapse.DEFAULTS, $this.data(), "object" == typeof option && option);
            !data && options.toggle && /show|hide/.test(option) && (options.toggle = !1), data || $this.data("bs.collapse", data = new Collapse(this, options)), 
            "string" == typeof option && data[option]();
        });
    }
    var Collapse = function(element, options) {
        this.$element = $(element), this.options = $.extend({}, Collapse.DEFAULTS, options), 
        this.$trigger = $('[data-toggle="collapse"][href="#' + element.id + '"],[data-toggle="collapse"][data-target="#' + element.id + '"]'), 
        this.transitioning = null, this.options.parent ? this.$parent = this.getParent() : this.addAriaAndCollapsedClass(this.$element, this.$trigger), 
        this.options.toggle && this.toggle();
    };
    Collapse.VERSION = "3.3.5", Collapse.TRANSITION_DURATION = 350, Collapse.DEFAULTS = {
        toggle: !0
    }, Collapse.prototype.dimension = function() {
        var hasWidth = this.$element.hasClass("width");
        return hasWidth ? "width" : "height";
    }, Collapse.prototype.show = function() {
        if (!this.transitioning && !this.$element.hasClass("in")) {
            var activesData, actives = this.$parent && this.$parent.children(".panel").children(".in, .collapsing");
            if (!(actives && actives.length && (activesData = actives.data("bs.collapse"), activesData && activesData.transitioning))) {
                var startEvent = $.Event("show.bs.collapse");
                if (this.$element.trigger(startEvent), !startEvent.isDefaultPrevented()) {
                    actives && actives.length && (Plugin.call(actives, "hide"), activesData || actives.data("bs.collapse", null));
                    var dimension = this.dimension();
                    this.$element.removeClass("collapse").addClass("collapsing")[dimension](0).attr("aria-expanded", !0), 
                    this.$trigger.removeClass("collapsed").attr("aria-expanded", !0), this.transitioning = 1;
                    var complete = function() {
                        this.$element.removeClass("collapsing").addClass("collapse in")[dimension](""), 
                        this.transitioning = 0, this.$element.trigger("shown.bs.collapse");
                    };
                    if (!$.support.transition) return complete.call(this);
                    var scrollSize = $.camelCase([ "scroll", dimension ].join("-"));
                    this.$element.one("bsTransitionEnd", $.proxy(complete, this)).emulateTransitionEnd(Collapse.TRANSITION_DURATION)[dimension](this.$element[0][scrollSize]);
                }
            }
        }
    }, Collapse.prototype.hide = function() {
        if (!this.transitioning && this.$element.hasClass("in")) {
            var startEvent = $.Event("hide.bs.collapse");
            if (this.$element.trigger(startEvent), !startEvent.isDefaultPrevented()) {
                var dimension = this.dimension();
                this.$element[dimension](this.$element[dimension]())[0].offsetHeight, this.$element.addClass("collapsing").removeClass("collapse in").attr("aria-expanded", !1), 
                this.$trigger.addClass("collapsed").attr("aria-expanded", !1), this.transitioning = 1;
                var complete = function() {
                    this.transitioning = 0, this.$element.removeClass("collapsing").addClass("collapse").trigger("hidden.bs.collapse");
                };
                return $.support.transition ? void this.$element[dimension](0).one("bsTransitionEnd", $.proxy(complete, this)).emulateTransitionEnd(Collapse.TRANSITION_DURATION) : complete.call(this);
            }
        }
    }, Collapse.prototype.toggle = function() {
        this[this.$element.hasClass("in") ? "hide" : "show"]();
    }, Collapse.prototype.getParent = function() {
        return $(this.options.parent).find('[data-toggle="collapse"][data-parent="' + this.options.parent + '"]').each($.proxy(function(i, element) {
            var $element = $(element);
            this.addAriaAndCollapsedClass(getTargetFromTrigger($element), $element);
        }, this)).end();
    }, Collapse.prototype.addAriaAndCollapsedClass = function($element, $trigger) {
        var isOpen = $element.hasClass("in");
        $element.attr("aria-expanded", isOpen), $trigger.toggleClass("collapsed", !isOpen).attr("aria-expanded", isOpen);
    };
    var old = $.fn.collapse;
    $.fn.collapse = Plugin, $.fn.collapse.Constructor = Collapse, $.fn.collapse.noConflict = function() {
        return $.fn.collapse = old, this;
    }, $(document).on("click.bs.collapse.data-api", '[data-toggle="collapse"]', function(e) {
        var $this = $(this);
        $this.attr("data-target") || e.preventDefault();
        var $target = getTargetFromTrigger($this), data = $target.data("bs.collapse"), option = data ? "toggle" : $this.data();
        Plugin.call($target, option);
    });
}(jQuery), +function($) {
    "use strict";
    function getParent($this) {
        var selector = $this.attr("data-target");
        selector || (selector = $this.attr("href"), selector = selector && /#[A-Za-z]/.test(selector) && selector.replace(/.*(?=#[^\s]*$)/, ""));
        var $parent = selector && $(selector);
        return $parent && $parent.length ? $parent : $this.parent();
    }
    function clearMenus(e) {
        e && 3 === e.which || ($(backdrop).remove(), $(toggle).each(function() {
            var $this = $(this), $parent = getParent($this), relatedTarget = {
                relatedTarget: this
            };
            $parent.hasClass("open") && (e && "click" == e.type && /input|textarea/i.test(e.target.tagName) && $.contains($parent[0], e.target) || ($parent.trigger(e = $.Event("hide.bs.dropdown", relatedTarget)), 
            e.isDefaultPrevented() || ($this.attr("aria-expanded", "false"), $parent.removeClass("open").trigger("hidden.bs.dropdown", relatedTarget))));
        }));
    }
    function Plugin(option) {
        return this.each(function() {
            var $this = $(this), data = $this.data("bs.dropdown");
            data || $this.data("bs.dropdown", data = new Dropdown(this)), "string" == typeof option && data[option].call($this);
        });
    }
    var backdrop = ".dropdown-backdrop", toggle = '[data-toggle="dropdown"]', Dropdown = function(element) {
        $(element).on("click.bs.dropdown", this.toggle);
    };
    Dropdown.VERSION = "3.3.5", Dropdown.prototype.toggle = function(e) {
        var $this = $(this);
        if (!$this.is(".disabled, :disabled")) {
            var $parent = getParent($this), isActive = $parent.hasClass("open");
            if (clearMenus(), !isActive) {
                "ontouchstart" in document.documentElement && !$parent.closest(".navbar-nav").length && $(document.createElement("div")).addClass("dropdown-backdrop").insertAfter($(this)).on("click", clearMenus);
                var relatedTarget = {
                    relatedTarget: this
                };
                if ($parent.trigger(e = $.Event("show.bs.dropdown", relatedTarget)), e.isDefaultPrevented()) return;
                $this.trigger("focus").attr("aria-expanded", "true"), $parent.toggleClass("open").trigger("shown.bs.dropdown", relatedTarget);
            }
            return !1;
        }
    }, Dropdown.prototype.keydown = function(e) {
        if (/(38|40|27|32)/.test(e.which) && !/input|textarea/i.test(e.target.tagName)) {
            var $this = $(this);
            if (e.preventDefault(), e.stopPropagation(), !$this.is(".disabled, :disabled")) {
                var $parent = getParent($this), isActive = $parent.hasClass("open");
                if (!isActive && 27 != e.which || isActive && 27 == e.which) return 27 == e.which && $parent.find(toggle).trigger("focus"), 
                $this.trigger("click");
                var desc = " li:not(.disabled):visible a", $items = $parent.find(".dropdown-menu" + desc);
                if ($items.length) {
                    var index = $items.index(e.target);
                    38 == e.which && index > 0 && index--, 40 == e.which && index < $items.length - 1 && index++, 
                    ~index || (index = 0), $items.eq(index).trigger("focus");
                }
            }
        }
    };
    var old = $.fn.dropdown;
    $.fn.dropdown = Plugin, $.fn.dropdown.Constructor = Dropdown, $.fn.dropdown.noConflict = function() {
        return $.fn.dropdown = old, this;
    }, $(document).on("click.bs.dropdown.data-api", clearMenus).on("click.bs.dropdown.data-api", ".dropdown form", function(e) {
        e.stopPropagation();
    }).on("click.bs.dropdown.data-api", toggle, Dropdown.prototype.toggle).on("keydown.bs.dropdown.data-api", toggle, Dropdown.prototype.keydown).on("keydown.bs.dropdown.data-api", ".dropdown-menu", Dropdown.prototype.keydown);
}(jQuery), +function($) {
    "use strict";
    function transitionEnd() {
        var el = document.createElement("bootstrap"), transEndEventNames = {
            WebkitTransition: "webkitTransitionEnd",
            MozTransition: "transitionend",
            OTransition: "oTransitionEnd otransitionend",
            transition: "transitionend"
        };
        for (var name in transEndEventNames) if (void 0 !== el.style[name]) return {
            end: transEndEventNames[name]
        };
        return !1;
    }
    $.fn.emulateTransitionEnd = function(duration) {
        var called = !1, $el = this;
        $(this).one("bsTransitionEnd", function() {
            called = !0;
        });
        var callback = function() {
            called || $($el).trigger($.support.transition.end);
        };
        return setTimeout(callback, duration), this;
    }, $(function() {
        $.support.transition = transitionEnd(), $.support.transition && ($.event.special.bsTransitionEnd = {
            bindType: $.support.transition.end,
            delegateType: $.support.transition.end,
            handle: function(e) {
                return $(e.target).is(this) ? e.handleObj.handler.apply(this, arguments) : void 0;
            }
        });
    });
}(jQuery), +function($) {
    "use strict";
    function Plugin(option, _relatedTarget) {
        return this.each(function() {
            var $this = $(this), data = $this.data("bs.modal"), options = $.extend({}, Modal.DEFAULTS, $this.data(), "object" == typeof option && option);
            data || $this.data("bs.modal", data = new Modal(this, options)), "string" == typeof option ? data[option](_relatedTarget) : options.show && data.show(_relatedTarget);
        });
    }
    var Modal = function(element, options) {
        this.options = options, this.$body = $(document.body), this.$element = $(element), 
        this.$dialog = this.$element.find(".modal-dialog"), this.$backdrop = null, this.isShown = null, 
        this.originalBodyPad = null, this.scrollbarWidth = 0, this.ignoreBackdropClick = !1, 
        this.options.remote && this.$element.find(".modal-content").load(this.options.remote, $.proxy(function() {
            this.$element.trigger("loaded.bs.modal");
        }, this));
    };
    Modal.VERSION = "3.3.5", Modal.TRANSITION_DURATION = 300, Modal.BACKDROP_TRANSITION_DURATION = 150, 
    Modal.DEFAULTS = {
        backdrop: !0,
        keyboard: !0,
        show: !0
    }, Modal.prototype.toggle = function(_relatedTarget) {
        return this.isShown ? this.hide() : this.show(_relatedTarget);
    }, Modal.prototype.show = function(_relatedTarget) {
        var that = this, e = $.Event("show.bs.modal", {
            relatedTarget: _relatedTarget
        });
        this.$element.trigger(e), this.isShown || e.isDefaultPrevented() || (this.isShown = !0, 
        this.checkScrollbar(), this.setScrollbar(), this.$body.addClass("modal-open"), this.escape(), 
        this.resize(), this.$element.on("click.dismiss.bs.modal", '[data-dismiss="modal"]', $.proxy(this.hide, this)), 
        this.$dialog.on("mousedown.dismiss.bs.modal", function() {
            that.$element.one("mouseup.dismiss.bs.modal", function(e) {
                $(e.target).is(that.$element) && (that.ignoreBackdropClick = !0);
            });
        }), this.backdrop(function() {
            var transition = $.support.transition && that.$element.hasClass("fade");
            that.$element.parent().length || that.$element.appendTo(that.$body), that.$element.show().scrollTop(0), 
            that.adjustDialog(), transition && that.$element[0].offsetWidth, that.$element.addClass("in"), 
            that.enforceFocus();
            var e = $.Event("shown.bs.modal", {
                relatedTarget: _relatedTarget
            });
            transition ? that.$dialog.one("bsTransitionEnd", function() {
                that.$element.trigger("focus").trigger(e);
            }).emulateTransitionEnd(Modal.TRANSITION_DURATION) : that.$element.trigger("focus").trigger(e);
        }));
    }, Modal.prototype.hide = function(e) {
        e && e.preventDefault(), e = $.Event("hide.bs.modal"), this.$element.trigger(e), 
        this.isShown && !e.isDefaultPrevented() && (this.isShown = !1, this.escape(), this.resize(), 
        $(document).off("focusin.bs.modal"), this.$element.removeClass("in").off("click.dismiss.bs.modal").off("mouseup.dismiss.bs.modal"), 
        this.$dialog.off("mousedown.dismiss.bs.modal"), $.support.transition && this.$element.hasClass("fade") ? this.$element.one("bsTransitionEnd", $.proxy(this.hideModal, this)).emulateTransitionEnd(Modal.TRANSITION_DURATION) : this.hideModal());
    }, Modal.prototype.enforceFocus = function() {
        $(document).off("focusin.bs.modal").on("focusin.bs.modal", $.proxy(function(e) {
            this.$element[0] === e.target || this.$element.has(e.target).length || this.$element.trigger("focus");
        }, this));
    }, Modal.prototype.escape = function() {
        this.isShown && this.options.keyboard ? this.$element.on("keydown.dismiss.bs.modal", $.proxy(function(e) {
            27 == e.which && this.hide();
        }, this)) : this.isShown || this.$element.off("keydown.dismiss.bs.modal");
    }, Modal.prototype.resize = function() {
        this.isShown ? $(window).on("resize.bs.modal", $.proxy(this.handleUpdate, this)) : $(window).off("resize.bs.modal");
    }, Modal.prototype.hideModal = function() {
        var that = this;
        this.$element.hide(), this.backdrop(function() {
            that.$body.removeClass("modal-open"), that.resetAdjustments(), that.resetScrollbar(), 
            that.$element.trigger("hidden.bs.modal");
        });
    }, Modal.prototype.removeBackdrop = function() {
        this.$backdrop && this.$backdrop.remove(), this.$backdrop = null;
    }, Modal.prototype.backdrop = function(callback) {
        var that = this, animate = this.$element.hasClass("fade") ? "fade" : "";
        if (this.isShown && this.options.backdrop) {
            var doAnimate = $.support.transition && animate;
            if (this.$backdrop = $(document.createElement("div")).addClass("modal-backdrop " + animate).appendTo(this.$body), 
            this.$element.on("click.dismiss.bs.modal", $.proxy(function(e) {
                return this.ignoreBackdropClick ? void (this.ignoreBackdropClick = !1) : void (e.target === e.currentTarget && ("static" == this.options.backdrop ? this.$element[0].focus() : this.hide()));
            }, this)), doAnimate && this.$backdrop[0].offsetWidth, this.$backdrop.addClass("in"), 
            !callback) return;
            doAnimate ? this.$backdrop.one("bsTransitionEnd", callback).emulateTransitionEnd(Modal.BACKDROP_TRANSITION_DURATION) : callback();
        } else if (!this.isShown && this.$backdrop) {
            this.$backdrop.removeClass("in");
            var callbackRemove = function() {
                that.removeBackdrop(), callback && callback();
            };
            $.support.transition && this.$element.hasClass("fade") ? this.$backdrop.one("bsTransitionEnd", callbackRemove).emulateTransitionEnd(Modal.BACKDROP_TRANSITION_DURATION) : callbackRemove();
        } else callback && callback();
    }, Modal.prototype.handleUpdate = function() {
        this.adjustDialog();
    }, Modal.prototype.adjustDialog = function() {
        var modalIsOverflowing = this.$element[0].scrollHeight > document.documentElement.clientHeight;
        this.$element.css({
            paddingLeft: !this.bodyIsOverflowing && modalIsOverflowing ? this.scrollbarWidth : "",
            paddingRight: this.bodyIsOverflowing && !modalIsOverflowing ? this.scrollbarWidth : ""
        });
    }, Modal.prototype.resetAdjustments = function() {
        this.$element.css({
            paddingLeft: "",
            paddingRight: ""
        });
    }, Modal.prototype.checkScrollbar = function() {
        var fullWindowWidth = window.innerWidth;
        if (!fullWindowWidth) {
            var documentElementRect = document.documentElement.getBoundingClientRect();
            fullWindowWidth = documentElementRect.right - Math.abs(documentElementRect.left);
        }
        this.bodyIsOverflowing = document.body.clientWidth < fullWindowWidth, this.scrollbarWidth = this.measureScrollbar();
    }, Modal.prototype.setScrollbar = function() {
        var bodyPad = parseInt(this.$body.css("padding-right") || 0, 10);
        this.originalBodyPad = document.body.style.paddingRight || "", this.bodyIsOverflowing && this.$body.css("padding-right", bodyPad + this.scrollbarWidth);
    }, Modal.prototype.resetScrollbar = function() {
        this.$body.css("padding-right", this.originalBodyPad);
    }, Modal.prototype.measureScrollbar = function() {
        var scrollDiv = document.createElement("div");
        scrollDiv.className = "modal-scrollbar-measure", this.$body.append(scrollDiv);
        var scrollbarWidth = scrollDiv.offsetWidth - scrollDiv.clientWidth;
        return this.$body[0].removeChild(scrollDiv), scrollbarWidth;
    };
    var old = $.fn.modal;
    $.fn.modal = Plugin, $.fn.modal.Constructor = Modal, $.fn.modal.noConflict = function() {
        return $.fn.modal = old, this;
    }, $(document).on("click.bs.modal.data-api", '[data-toggle="modal"]', function(e) {
        var $this = $(this), href = $this.attr("href"), $target = $($this.attr("data-target") || href && href.replace(/.*(?=#[^\s]+$)/, "")), option = $target.data("bs.modal") ? "toggle" : $.extend({
            remote: !/#/.test(href) && href
        }, $target.data(), $this.data());
        $this.is("a") && e.preventDefault(), $target.one("show.bs.modal", function(showEvent) {
            showEvent.isDefaultPrevented() || $target.one("hidden.bs.modal", function() {
                $this.is(":visible") && $this.trigger("focus");
            });
        }), Plugin.call($target, option, this);
    });
}(jQuery), /*! */
/*! Minaraad */
function() {
    "use strict";
    $(function() {
        $(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function(evt) {
            setTimeout(function() {
                $(".masonry").masonry();
            }, 200);
        }), $(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function(evt) {
            setTimeout(function() {
                $(".masonry").masonry();
            }, 1e3);
        });
        var owner = $("#owner"), drawer = $("#drawer");
        $("html body");
        $(owner).find("a.more").click(function() {
            return $(owner).hide("fast"), $(drawer).slideDown("slow"), $("html, body").animate({
                scrollTop: $(document).height()
            }, "slow"), !1;
        }), $(drawer).find("a.less").click(function() {
            return $(drawer).hide("fast"), $(owner).slideDown("fast"), !1;
        }), $(".btn-search").click(function() {
            $(".search").slideToggle("fast", function() {
                $(".form-control").focus();
            });
        }), setTimeout(function() {
            $(".masonry").masonry({
                itemSelector: ".grid-item",
                columnWidth: ".grid-item",
                percentPosition: !0
            });
        }, 200);
        var common_content_filter = "#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info";
        $("#mailchimp_link a").prepOverlay({
            subtype: "ajax",
            filter: common_content_filter,
            formselector: "form#newsletter-subscriber-form",
            noform: function(el) {
                return $.plonepopups.noformerrorshow(el, "close");
            }
        }), $("#newsletter-mailchimp_link a").prepOverlay({
            subtype: "ajax",
            filter: common_content_filter,
            formselector: "form#newsletter-subscriber-form",
            noform: function(el) {
                return $.plonepopups.noformerrorshow(el, "close");
            }
        }), $("#login_link a").prepOverlay({
            subtype: "ajax",
            filter: common_content_filter,
            noform: function(el) {
                return $.plonepopups.noformerrorshow(el, "close");
            }
        });
    }), $(function($) {
        if ("undefined" != typeof event_attendees) {
            var cookie = $.cookie("minaraad_attendee");
            if (cookie) {
                '"' === cookie[0] && (cookie = cookie.slice(1)), '"' === cookie[cookie.length - 1] && (cookie = cookie.slice(0, cookie.length - 1));
                var cookie_parts = cookie.split("#");
                if (5 === cookie_parts.length) {
                    var hexdigest = cookie_parts[0];
                    if (32 === hexdigest.length) {
                        for (var subscribed = !1, index = 0; index < event_attendees.length; index++) if (event_attendees[index] === hexdigest) {
                            subscribed = !0;
                            break;
                        }
                        subscribed ? ($("#inschrijven").hide(), $("#subscribe_button").hide(), $("#unsubscribe_button").show()) : ($("#firstname").attr("value") || $("#firstname").attr("value", cookie_parts[1]), 
                        $("#lastname").attr("value") || $("#lastname").attr("value", cookie_parts[2]), $("#email").attr("value") || $("#email").attr("value", cookie_parts[3]), 
                        $("#work").attr("value") || $("#work").attr("value", cookie_parts[4]));
                    }
                }
            }
        }
    }), $(function($) {
        var dest, content, location, stack, oltoc, numdigits, wlh, target, targetOffset;
        if (dest = $("nav.toc section.nav-list div.nav-items"), content = $(".container article:first"), 
        content && dest.length && (dest.empty(), location = window.location.href, window.location.hash && (location = location.substring(0, location.lastIndexOf(window.location.hash))), 
        stack = [], $(content).find("*").not(".comment > h3").filter(function() {
            return /^h[1234]$/.test(this.tagName.toLowerCase());
        }).not(".documentFirstHeading").each(function(i) {
            var level, ol, li;
            for (level = this.nodeName.charAt(1); stack.length < level; ) ol = $("<ul>"), stack.length && (li = $(stack[stack.length - 1]).children("li:last"), 
            li.length || (li = $("<li>").appendTo($(stack[stack.length - 1]))), li.append(ol)), 
            stack.push(ol);
            for (;stack.length > level; ) stack.pop();
            $(this).before($('<a name="section-' + i + '" />')), $("<li>").append($("<a />").attr("href", location + "#section-" + i).text($(this).text())).appendTo($(stack[stack.length - 1]));
        }), stack.length)) {
            var oltoc = $(stack[0]), i = 1;
            i <= stack.length && $("nav.toc").show(), numdigits = oltoc.children().length.toString().length, 
            oltoc.addClass("TOC" + numdigits + "Digit"), dest.append(oltoc), wlh = window.location.hash, 
            wlh && (target = $(wlh), target = target.length && target || $('[name="' + wlh.slice(1) + '"]'), 
            targetOffset = target.offset(), targetOffset && $("html,body").animate({
                scrollTop: targetOffset.top
            }, 0));
        }
    });
}();