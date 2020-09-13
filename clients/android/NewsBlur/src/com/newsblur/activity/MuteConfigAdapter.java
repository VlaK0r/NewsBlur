package com.newsblur.activity;

import android.content.Context;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.ImageView;

import com.newsblur.R;
import com.newsblur.domain.Feed;
import com.newsblur.util.FeedUtils;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

public class MuteConfigAdapter extends FeedChooserAdapter {

    MuteConfigAdapter(Context context) {
        super(context);
    }

    @Override
    public View getGroupView(final int groupPosition, boolean isExpanded, View convertView, final ViewGroup parent) {
        View groupView = super.getGroupView(groupPosition, isExpanded, convertView, parent);

        groupView.setOnClickListener(v -> {
            ArrayList<Feed> folderChild = MuteConfigAdapter.this.folderChildren.get(groupPosition);
            boolean allAreMute = true;
            for (Feed feed : folderChild) {
                if (feed.active) {
                    allAreMute = false;
                    break;
                }
            }

            Set<String> feedIds = new HashSet<>(folderChild.size());
            for (Feed feed : folderChild) {
                // flip active flag
                feed.active = allAreMute;
                feedIds.add(feed.feedId);
            }

            // if allAreMute initially, we need to unMute feeds
            if (allAreMute) FeedUtils.unmuteFeeds(groupView.getContext(), feedIds);
            else FeedUtils.muteFeeds(groupView.getContext(), feedIds);
            notifyDataChanged();
        });
        return groupView;
    }

    @Override
    public View getChildView(int groupPosition, int childPosition, boolean isLastChild, View convertView, final ViewGroup parent) {
        View childView = super.getChildView(groupPosition, childPosition, isLastChild, convertView, parent);
        final Feed feed = folderChildren.get(groupPosition).get(childPosition);
        final CheckBox checkBox = childView.findViewById(R.id.check_box);
        final ImageView imgToggle = childView.findViewById(R.id.img_toggle);
        checkBox.setVisibility(View.GONE);
        imgToggle.setVisibility(View.VISIBLE);

        if (feed.active) imgToggle.setBackgroundResource(R.drawable.mute_feed_on);
        else imgToggle.setBackgroundResource(R.drawable.mute_feed_off);

        childView.setOnClickListener(v -> {
            feed.active = !feed.active;
            Set<String> feedIds = new HashSet<>(1);
            feedIds.add(feed.feedId);
            if (feed.active) FeedUtils.unmuteFeeds(childView.getContext(), feedIds);
            else FeedUtils.muteFeeds(childView.getContext(), feedIds);
            notifyDataChanged();
        });
        return childView;
    }
}