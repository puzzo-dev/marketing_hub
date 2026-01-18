# Portal Design System - Testing Checklist

## Pre-Testing Setup
- [x] Build completed: `bench build --app marketing_hub`
- [x] Cache cleared: `bench --site erpnext-v15.local clear-cache`
- [ ] Frappe dev server running
- [ ] Browser dev tools ready

## Page Navigation Tests

### Dashboard (`/marketing`)
- [ ] Page loads without errors
- [ ] Header displays "Marketing Dashboard"
- [ ] Stats grid shows 4 metrics (Spend, Campaigns, Revenue, Leads)
- [ ] "New Campaign" button visible in header
- [ ] Active campaigns section displays (or shows empty state)
- [ ] Quick links cards visible (Campaigns, Social Media, Analytics)
- [ ] All links functional

### Campaigns (`/marketing/campaigns`)
- [ ] Page loads without errors
- [ ] Header displays "Campaigns"
- [ ] "New Campaign" button in header
- [ ] Campaign cards display in grid (if campaigns exist)
- [ ] Each card shows: Name, Status badge, Dates, Spend, Revenue, ROAS
- [ ] ROAS color coding: Green (≥2), Orange (≥1), Default (<1)
- [ ] "View Details" button links to desk
- [ ] Empty state displays if no campaigns

### Social Posts (`/marketing/social`)
- [ ] Page loads without errors
- [ ] Header displays "Social Media Posts"
- [ ] "Create Post" button in header
- [ ] Stats grid shows 4 metrics
- [ ] Filter buttons visible (All, Draft, Scheduled, Published)
- [ ] Post cards display in grid
- [ ] Platform and status badges visible
- [ ] Media images load correctly
- [ ] Engagement metrics show for published posts
- [ ] Filter buttons work (JavaScript)
- [ ] Empty state if no posts

### Analytics (`/marketing/analytics`)
- [ ] Page loads without errors
- [ ] Header displays "Analytics"
- [ ] Connector status cards display
- [ ] Sync status badges correct color
- [ ] Performance table displays
- [ ] Table headers: Channel, Spend, Revenue, ROAS, CTR, Conv.
- [ ] ROAS color coding in table
- [ ] Table responsive on mobile
- [ ] Empty state if no data

## Component Tests

### App Switcher Dropdown
- [ ] Dropdown button visible in header
- [ ] Grid icon displays correctly
- [ ] Dropdown opens on click
- [ ] "Desk" link works → `/app`
- [ ] "Portal" link active and works → `/marketing`
- [ ] "Settings" link works → `/app/user`
- [ ] Dropdown closes after selection

### Navigation
- [ ] All internal links work
- [ ] Back/forward browser navigation
- [ ] Breadcrumb navigation (if added)
- [ ] Deep links work (direct URL access)

### Icons
- [ ] Plus icon (`#icon-plus`) displays
- [ ] Calendar icon (`#icon-calendar`) displays
- [ ] Target icon (`#icon-target`) displays
- [ ] Share icon (`#icon-share-2`) displays
- [ ] Chart icon (`#icon-bar-chart-2`) displays
- [ ] Edit icon (`#icon-edit`) displays
- [ ] Grid icon (`#icon-grid`) displays
- [ ] All icons are SVG (not missing)

### Badges
- [ ] Success badges (green) display correctly
- [ ] Warning badges (orange) display correctly
- [ ] Info badges (blue) display correctly
- [ ] Secondary badges (gray) display correctly
- [ ] Badge text readable

### Cards
- [ ] Stat cards display with proper spacing
- [ ] Campaign cards have consistent height
- [ ] Social post cards show images properly
- [ ] Card hover effects work
- [ ] Cards responsive on mobile

### Buttons
- [ ] Primary buttons styled correctly
- [ ] Default buttons styled correctly
- [ ] Small button sizing correct
- [ ] Button icons aligned
- [ ] Hover states work
- [ ] Active states work

### Tables
- [ ] Table headers styled
- [ ] Table rows hover effect
- [ ] Text alignment correct (right for numbers)
- [ ] Mobile: Horizontal scroll works
- [ ] Desktop: Full width display

## Responsive Design Tests

### Desktop (≥1200px)
- [ ] 4-column stats grid
- [ ] 3-column campaign/post grids
- [ ] Full-width container
- [ ] Table displays all columns
- [ ] Header actions inline

### Tablet (768px - 1199px)
- [ ] 2-column stats grid
- [ ] 2-column campaign/post grids
- [ ] Proper spacing maintained
- [ ] Table scrolls horizontally

### Mobile (< 768px)
- [ ] 1-column stats grid
- [ ] 1-column campaign/post grids
- [ ] Header stacks vertically
- [ ] Buttons full width
- [ ] Table scrolls smoothly
- [ ] Text readable without zoom
- [ ] Touch targets large enough (44px min)

## CSS & Styling Tests

### Frappe Variables
- [ ] `--card-bg` applied correctly
- [ ] `--border-color` consistent
- [ ] `--text-muted` for secondary text
- [ ] `--heading-color` for titles
- [ ] Color variables match Frappe theme

### Bootstrap Classes
- [ ] `.container` centers content
- [ ] `.row` / `.col-*` grid works
- [ ] `.d-flex` utilities functional
- [ ] `.text-*` color classes work
- [ ] `.mb-*` / `.mt-*` spacing consistent
- [ ] `.btn` classes styled correctly

### Custom Classes
- [ ] `.marketing-stats-grid` displays correctly
- [ ] `.campaign-grid` layout works
- [ ] `.posts-grid` layout works
- [ ] `.stat-card` styling consistent

## Browser Compatibility

### Chrome/Edge (Chromium)
- [ ] All features work
- [ ] CSS Grid displays correctly
- [ ] Flexbox layouts correct
- [ ] Icons display

### Firefox
- [ ] All features work
- [ ] CSS Grid displays correctly
- [ ] Flexbox layouts correct
- [ ] Icons display

### Safari
- [ ] All features work
- [ ] CSS Grid displays correctly
- [ ] Flexbox layouts correct
- [ ] Icons display

## Performance Tests

### Load Time
- [ ] Initial page load < 2s
- [ ] Assets cached properly
- [ ] Images lazy load (if applicable)
- [ ] No console errors

### Console Checks
- [ ] No JavaScript errors
- [ ] No CSS errors
- [ ] No 404 errors (missing assets)
- [ ] No CORS errors

## Accessibility Tests

### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Focus indicators visible
- [ ] Dropdown keyboard accessible
- [ ] Skip links present (Frappe default)

### Screen Reader
- [ ] Page title announced
- [ ] Headings have hierarchy (h1 > h2 > h3)
- [ ] Buttons have accessible labels
- [ ] Links have descriptive text
- [ ] Images have alt text

### Contrast
- [ ] Text meets WCAG AA (4.5:1)
- [ ] Buttons meet contrast requirements
- [ ] Focus indicators visible

## Data Tests

### With Data
- [ ] Stats display correct numbers
- [ ] Campaign cards show real data
- [ ] Social posts show real content
- [ ] Analytics table populated
- [ ] Dates format correctly
- [ ] Currency formats correctly

### Empty States
- [ ] Dashboard shows empty state if needed
- [ ] Campaigns shows "No campaigns" message
- [ ] Social shows "No posts" message
- [ ] Analytics shows "No data" message
- [ ] Empty state CTAs work

## Edge Cases

### Long Content
- [ ] Long campaign names truncate/wrap
- [ ] Long social post content truncates
- [ ] Tables handle overflow
- [ ] Cards maintain height

### Missing Data
- [ ] Handles null/undefined gracefully
- [ ] Missing images show placeholder
- [ ] Missing stats show 0 or "N/A"
- [ ] No template errors

### Error States
- [ ] Network errors handled
- [ ] Invalid URLs redirect
- [ ] Permission errors show message

## Documentation Verification

- [x] `PORTAL_DESIGN_REFACTOR.md` created
- [x] `DESIGN_BEFORE_AFTER.md` created
- [ ] Screenshots captured
- [ ] Known issues documented
- [ ] Deployment notes complete

## Final Checks

- [ ] All critical paths tested
- [ ] No blocking issues found
- [ ] Performance acceptable
- [ ] Ready for user testing
- [ ] Deployment approved

## Known Issues

*(Document any issues found during testing)*

1.
2.
3.

## Notes

*(Any additional observations)*

---

**Tester**: _______________
**Date**: _______________
**Browser/Device**: _______________
**Result**: ☐ Pass ☐ Fail ☐ Pass with Issues
