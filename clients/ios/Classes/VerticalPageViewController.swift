//
//  VerticalPageViewController.swift
//  NewsBlur
//
//  Created by David Sinclair on 2020-09-24.
//  Copyright © 2020 NewsBlur. All rights reserved.
//

import UIKit

/// Manages vertical story pages. Instances of this are contained within `HorizontalPageViewController`.
class VerticalPageViewController: UIPageViewController {
    /// Weak reference to owning horizontal page view controller.
    weak var horizontalPageViewController: HorizontalPageViewController?
    
    /// Weak computed reference to owning detail view controller.
    weak var detailViewController: DetailViewController? {
        return horizontalPageViewController?.detailViewController
    }
    
    /// Returns the story page index of the currently displayed page.
    var pageIndex: Int? {
        guard let current = currentController else {
            return nil
        }
        
        return current.pageIndex
    }
    
    /// The currently displayed story view controller. Call `setCurrentController(_:direction:animated:completion:)` instead to animate to the page. Shouldn't be `nil`, but could be if not set up yet.
    var currentController: StoryDetailViewController? {
        get {
            return viewControllers?.first as? StoryDetailViewController
        }
        set {
            if let viewController = newValue {
                setCurrentController(viewController)
            }
        }
    }
    
    /// The previous story view controller, if it has been requested, otherwise `nil`.
    var previousController: StoryDetailViewController?
    
    /// The next story view controller, if it has been requested, otherwise `nil`.
    var nextController: StoryDetailViewController?
    
    /// Clear the previous and next story view controllers.
    func reset() {
        previousController = nil
        nextController = nil
    }
    
    /// Sets the currently displayed story view controller.
    ///
    /// - Parameter controller: The story view controller to display.
    /// - Parameter direction: The navigation direction. Defaults to `.forward`.
    /// - Parameter animated: Whether or not to animate it. Defaults to `false`.
    /// - Parameter completion: A closure to call when the animation completes. Defaults to `nil`.
    func setCurrentController(_ controller: StoryDetailViewController, direction: UIPageViewController.NavigationDirection = .forward, animated: Bool = false, completion: ((Bool) -> Void)? = nil) {
        setViewControllers([controller], direction: direction, animated: animated, completion: completion)
    }
    
    override func setViewControllers(_ viewControllers: [UIViewController]?, direction: UIPageViewController.NavigationDirection, animated: Bool, completion: ((Bool) -> Void)? = nil) {
        reset()
        
        super.setViewControllers(viewControllers, direction: direction, animated: animated, completion: completion)
    }
}